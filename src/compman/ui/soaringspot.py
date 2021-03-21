import logging
from typing import List

import urwid

from compman import soaringspot, storage
from compman.ui import widget
from compman.ui.activity import Activity

log = logging.getLogger("compman")


class SoaringSpotPicker(urwid.ListBox):
    signals = ["select", "focus"]

    def __init__(self, activity: Activity) -> None:
        self._items = urwid.SimpleListWalker([])
        super().__init__(self._items)
        self.activity = activity
        activity.async_task(self._download_competitions())

    def set_competitions(
        self, competitions: List[soaringspot.SoaringSpotContest]
    ) -> None:
        del self._items[:]
        if not competitions:
            return

        self.competitions = competitions
        for comp in competitions:
            btn = widget.CMSelectableListItem(comp.title)
            urwid.connect_signal(btn, "click", self._on_competition_selected, comp)
            self._items.extend([btn])
        urwid.connect_signal(self._items, "modified", self._on_focus_changed)
        self._emit("focus", competitions[0])

    async def _download_competitions(self):
        del self._items[:]
        statusitem = urwid.Text(("progress", "Downloading..."))
        self._items.append(statusitem)
        try:
            comps = await soaringspot.fetch_competitions()
        except soaringspot.SoaringSpotClientError as e:
            statusitem.set_text(
                ("error message", f"Error downloading competition list: {e}")
            )
            log.exception("Error downloading competition list")
            return
        self.set_competitions(comps)

    def _on_competition_selected(
        self, btn: urwid.Widget, sscomp: soaringspot.SoaringSpotContest
    ) -> None:
        comp = storage.load_competition(sscomp.id)
        if comp is not None:
            comp.title = sscomp.title
            comp.soaringspot_url = sscomp.href
        else:
            comp = storage.StoredCompetition(
                id=sscomp.id, title=sscomp.title, soaringspot_url=sscomp.href
            )
        storage.save_competition(comp)
        self._emit("select", comp)

    def _on_focus_changed(self):
        focused, idx = self.get_focus()
        selected = self.competitions[idx]
        self._emit("focus", selected)


class SoaringSpotPickerScreen(Activity):
    def create_view(self):
        mainview = SoaringSpotPicker(self)
        urwid.connect_signal(mainview, "select", self._on_competition_selected)
        urwid.connect_signal(mainview, "focus", self._on_comp_focused)
        self.footer = urwid.Text("")

        return urwid.Frame(
            widget.CMScreenPadding(mainview),
            header=widget.CMScreenHeader("Pick a new competition"),
            footer=widget.CMScreenPadding(self.footer),
        )

    def _on_competition_selected(self, ev, comp):
        self.finish(comp)

    def _on_comp_focused(self, ev, comp):
        self.footer.set_text(comp.description)

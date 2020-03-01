from typing import List
import asyncio

import urwid

from compman.ui import widget
from compman import soaringspot
from compman import storage
from compman import config


class SoaringSpotPicker(urwid.ListBox):
    signals = ["select", "focus"]

    def __init__(self) -> None:
        self._items = urwid.SimpleListWalker([])
        super().__init__(self._items)
        asyncio.create_task(self._download_competitions())

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

            # txt = urwid.Padding(
            #     urwid.AttrMap(urwid.Text(comp.description), "text"), left=2
            # )
            self._items.extend([btn])
        urwid.connect_signal(self._items, "modified", self._on_focus_changed)
        self._emit("focus", competitions[0])

    async def _download_competitions(self):
        del self._items[:]
        progressbar = urwid.ProgressBar("pg normal", "pg complete")
        self._items.extend([urwid.Text("Downloading..."), progressbar])
        comps = await soaringspot.fetch_competitions()
        self.set_competitions(comps)

    def _on_competition_selected(
        self, btn: urwid.Widget, sscomp: soaringspot.SoaringSpotContest
    ) -> None:
        comp = storage.StoredCompetition(
            id=sscomp.id, title=sscomp.title, soaringspot_url=sscomp.href
        )
        storage.save_competition(comp)
        self._emit("select", comp)

    def _on_focus_changed(self):
        focused, idx = self.get_focus()
        selected = self.competitions[idx]
        self._emit("focus", selected)


class SoaringSpotPickerScreen:
    def __init__(self, container):
        container.original_widget = self._create_view()
        self.response = asyncio.Future()

    def _create_view(self):
        mainview = SoaringSpotPicker()
        urwid.connect_signal(mainview, "select", self._on_competition_selected)
        urwid.connect_signal(mainview, "focus", self._on_comp_focused)
        self.footer = urwid.Text("")

        return urwid.Frame(
            urwid.Padding(mainview, left=2, right=2),
            header=urwid.Text("Pick a new competition"),
            footer=urwid.LineBox(self.footer),
        )

    def _on_competition_selected(self, ev, comp):
        config.get().current_competition_id = comp.id
        config.save()
        self.response.set_result(comp)

    def _on_comp_focused(self, ev, comp):
        self.footer.set_text(comp.description)

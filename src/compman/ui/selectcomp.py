import logging

import urwid

from compman.ui import widget
from compman.ui.activity import Activity
from compman import storage


log = logging.getLogger("compman")


class SelectCompetitionScreen(Activity):
    def create_view(self):
        self._items = []
        self._populate_stored_comps()
        picker = urwid.Pile(self._items)

        add_btn = widget.CMButton("New competition")
        self.connect_async(add_btn, "click", self._on_new_competition)
        cancel_btn = widget.CMButton("Cancel")
        urwid.connect_signal(cancel_btn, "click", self._on_cancel)

        buttons = urwid.GridFlow([add_btn, cancel_btn], 22, 2, 1, "left")

        mainview = urwid.Pile([picker, urwid.Divider(), buttons])

        return urwid.Frame(
            urwid.Filler(widget.CMScreenPadding(mainview), valign=urwid.TOP),
            header=widget.CMScreenHeader("Switch competition"),
        )

    def _populate_stored_comps(self):
        for comp in storage.list_competitions():
            btn = widget.CMSelectableListItem(comp.title)
            urwid.connect_signal(btn, "click", self._on_competition_selected, comp)
            self._items.append(btn)

    def _on_competition_selected(self, btn, comp):
        self._comp_selected(comp)

    async def _on_new_competition(self):
        from compman.ui.soaringspot import SoaringSpotPickerScreen

        screen = SoaringSpotPickerScreen(self.container)
        res = await self.run_activity(screen)
        if res is not None:
            self._comp_selected(res)

    def _comp_selected(self, comp):
        storage.get_settings().current_competition_id = comp.id
        storage.save_settings()

        self.finish(comp)

        from compman.ui.compdetails import CompetitionDetailsScreen

        details = CompetitionDetailsScreen(self.container)
        details.show()

    def _on_cancel(self, btn):
        self.finish(None)

import asyncio
import logging

import urwid
from compman.ui import widget
from compman import storage


log = logging.getLogger("compman")


class SelectCompetitionScreen:
    def __init__(self, container):
        container.original_widget = self._create_view()
        self.container = container
        self.response = asyncio.Future()

    def _create_view(self):
        self._items = []
        self._populate_stored_comps()
        picker = urwid.Pile(self._items)

        add_btn = widget.CMButton("New competition")
        urwid.connect_signal(add_btn, "click", self._on_new_competition)
        cancel_btn = widget.CMButton("Cancel")
        urwid.connect_signal(cancel_btn, "click", self._on_cancel)

        buttons = urwid.GridFlow([add_btn, cancel_btn], 22, 2, 1, "left")

        mainview = urwid.Pile([picker, urwid.Divider(), buttons])

        return urwid.Frame(
            urwid.Filler(mainview, valign=urwid.TOP),
            header=urwid.Text("Switch competition"),
        )

    def _populate_stored_comps(self):
        for comp in storage.list_competitions():
            btn = widget.CMSelectableListItem(comp.title)
            urwid.connect_signal(btn, "click", self._on_competition_selected, comp)
            self._items.append(btn)

    def _on_competition_selected(self, btn, comp):
        self.response.set_result(comp)

    def _on_new_competition(self, btn):
        self._picker_task = asyncio.create_task(self._pick_soaringspot_comp())

    async def _pick_soaringspot_comp(self):
        from compman.ui.soaringspot import SoaringSpotPickerScreen

        screen = SoaringSpotPickerScreen(self.container)
        comp = await screen.response
        self.response.set_result(comp)

    def _on_cancel(self, btn):
        self.response.set_result(None)

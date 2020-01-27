from typing import List
import asyncio

import urwid

from compman.ui import widget
from compman import soaringspot
from compman import storage


class SoaringSpotPicker(urwid.ListBox):
    def __init__(self) -> None:
        self._items = urwid.SimpleListWalker([])
        super().__init__(self._items)
        asyncio.create_task(self._download_competitions())

    def set_competitions(
        self, competitions: List[soaringspot.SoaringSpotContest]
    ) -> None:
        del self._items[:]
        for comp in competitions:
            btn = widget.CMSelectableListItem(comp.title)
            urwid.connect_signal(btn, "click", self._handle_register_competition, comp)

            txt = urwid.Padding(
                urwid.AttrMap(urwid.Text(comp.description), "text"), left=2
            )
            self._items.extend([btn, txt])

    async def _download_competitions(self):
        del self._items[:]
        progressbar = urwid.ProgressBar("pg normal", "pg complete")
        self._items.extend([urwid.Text("Downloading..."), progressbar])
        comps = await soaringspot.fetch_competitions()
        self.set_competitions(comps)

    def _handle_register_competition(
        self, btn: urwid.Widget, sscomp: soaringspot.SoaringSpotContest
    ) -> None:
        comp = storage.StoredCompetition(id=sscomp.id, title=sscomp.title, soaringspot_url=sscomp.href)
        storage.save_competition(comp)

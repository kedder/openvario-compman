from typing import List
import asyncio
from dataclasses import dataclass

import urwid

from compman.ui import widget


@dataclass
class SoaringSpotCompetition:
    title: str
    description: str


class SoaringSpotPicker(urwid.ListBox):
    def __init__(self) -> None:
        self._items = urwid.SimpleListWalker([])
        super().__init__(self._items)
        asyncio.create_task(self._download_competitions())

    def set_competitions(self, competitions: List[SoaringSpotCompetition]) -> None:
        del self._items[:]
        for comp in competitions:
            btn = widget.CMSelectableListItem(comp.title)
            txt = urwid.Padding(
                urwid.AttrMap(urwid.Text(comp.description), "text"), left=2
            )
            self._items.extend([btn, txt])

    async def _download_competitions(self):
        del self._items[:]
        progressbar = urwid.ProgressBar("pg normal", "pg complete")

        self._items.extend([urwid.Text("Downloading..."), progressbar])

        for x in range(101):
            progressbar.set_completion(x)
            await asyncio.sleep(0.01)

        comp1 = SoaringSpotCompetition(
            "58 Campeonato Nacional 15 Andes Open",
            "Municipal de Vitacura, Chile,  18 January 2020 – 25 January 2020; 13 competitors in 1 classes",
        )

        comp2 = SoaringSpotCompetition(
            "Naviter Test Competition",
            "Bovec Letalisce, Slovenia,  1 January 2020 – 18 January 2020; 14 competitors in 1 classes",
        )

        comp3 = SoaringSpotCompetition(
            "10th FAI Women's World Gliding Championship",
            "Lake Keepit, Australia,  3 January 2020 – 17 January 2020; 47 competitors in 3 classes",
        )

        self.set_competitions([comp1, comp2, comp3])

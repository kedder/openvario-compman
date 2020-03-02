"""Welcome screen"""
import urwid

import compman
from compman import storage
from compman.ui import widget
from compman.ui.activity import Activity


class WelcomeScreen(Activity):
    def create_view(self):
        btxt = urwid.BigText("Compman", urwid.font.Thin6x6Font())
        hpad = urwid.Padding(urwid.AttrMap(btxt, "screen header"), "center", "clip")

        intro_text = [
            "Welcome to ",
            ("screen header", "Competition Manager"),
            f" version {compman.__version__}",
            "! ",
            "This app allows you to keep your contest files, ",
            "such as airspace or turnpoint, up to date. ",
            "To begin, pick your competition.",
        ]

        add_comp_button = widget.CMButton("Set Up a Competition")
        self.connect_async(add_comp_button, "click", self._pick_competition)

        intro = urwid.Padding(
            urwid.Pile(
                [
                    urwid.Divider(),
                    urwid.Text(intro_text),
                    urwid.Divider(),
                    urwid.GridFlow([add_comp_button], 24, 2, 1, "left"),
                    urwid.Divider(),
                ]
            ),
            left=1,
            right=1,
        )

        view = urwid.Filler(
            urwid.Pile(
                [
                    hpad,
                    urwid.Padding(
                        urwid.LineBox(intro, "Welcome!", title_align="left"),
                        width=("relative", 80),
                        align="center",
                    ),
                ]
            ),
            "middle",
        )

        return view

    async def _pick_competition(self):
        from compman.ui.soaringspot import SoaringSpotPickerScreen

        comp = await self.run_activity(SoaringSpotPickerScreen(self.container))
        if comp is None:
            return

        storage.get_settings().current_competition_id = comp.id
        storage.save_settings()
        self.finish(comp)

        from compman.ui.compdetails import CompetitionDetailsScreen

        details = CompetitionDetailsScreen(self.container)
        details.show()

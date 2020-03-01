"""Welcome screen"""
import urwid
from compman.ui import widget
from compman.ui.activity import Activity


class WelcomeScreen(Activity):
    def create_view(self):
        btxt = urwid.BigText(u"Compman", urwid.font.Thin6x6Font())
        hpad = urwid.Padding(btxt, "center", "clip")

        intro_text = [
            "Welcome to Competition Manager! ",
            "This app allows you to keep your contest files, ",
            "such as airspace or turnpoint, up to date. ",
            "To begin, pick your competition.",
        ]


        add_comp_button = widget.CMButton("Add a Competition")
        self.connect_async(add_comp_button, "click", self._pick_competition)

        intro = urwid.Padding(
            urwid.Pile(
                [
                    urwid.Divider(),
                    urwid.Text(intro_text),
                    urwid.Divider(),
                    urwid.GridFlow(
                        [add_comp_button], 19, 2, 1, "left"
                    ),
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
        res = await self.run_activity(SoaringSpotPickerScreen(self.container))
        if res is not None:
            self.finish(res)

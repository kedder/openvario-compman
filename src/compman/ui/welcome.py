"""Welcome screen"""
import asyncio

import urwid
from compman.ui import widget


class WelcomeScreen:
    def __init__(self, container):
        container.original_widget = self._create_view()
        self.container = container
        self.response = asyncio.Future()

    def _create_view(self):
        btxt = urwid.BigText(u"Compman", urwid.font.Thin6x6Font())
        hpad = urwid.Padding(btxt, "center", "clip")

        intro_text = [
            "Welcome to Competition Manager! ",
            "This app allows you to keep your contest files, ",
            "such as airspace or turnpoint, up to date. ",
            "To begin, pick your competition.",
        ]


        add_comp_button = widget.CMButton("Add a Competition")
        # urwid.connect_signal(add_comp_button, "click", self._handle_add_button)
        urwid.connect_signal(add_comp_button, "click", self._async, self._pick_competition)

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

    def __del__(self):
        print("DROPPED WELCOME SCREEN")

    def _async(self, ev, task):
        asyncio.create_task(task())

    async def _pick_competition(self):
        from compman.ui.soaringspot import SoaringSpotPickerScreen
        screen = SoaringSpotPickerScreen(self.container)
        res = await screen.response
        self.response.set_result(res)
        # self.response.set_result("HELLO WORLD")

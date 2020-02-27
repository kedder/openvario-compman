"""Welcome screen"""
import urwid
from compman.ui import widget


class WelcomeScreen:
    def __init__(self):
        self.view = self.create_view()

    def create_view(self):
        btxt = urwid.BigText(u"Comp Manager", urwid.font.Thin6x6Font())
        hpad = urwid.Padding(btxt, "center", "clip")

        intro_text = [
            "Welcome to Competition Manager! ",
            "This app allows you to keep your contenst files, ",
            "like airspaces or turnpoint up to date. ",
            "To begin, pick your competition.",
        ]

        intro = urwid.Padding(
            urwid.Pile(
                [
                    urwid.Divider(),
                    urwid.Text(intro_text),
                    urwid.Divider(),
                    urwid.GridFlow(
                        [widget.CMButton("Add Competition")], 15, 2, 1, "left"
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
            "top",
        )

        return view

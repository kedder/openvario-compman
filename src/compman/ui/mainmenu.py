import asyncio

import urwid
from compman.ui import widget
from compman.ui.compdetails import CompetitionDetailsScreen

class MainMenuScreen:
    def __init__(self, container):
        self.view = self._create_view()
        container.original_widget = self.view
        self.container = container
        self.response = asyncio.Future()

    def _create_view(self):
        btxt = urwid.BigText(u"Compman", urwid.font.Thin6x6Font())
        hpad = urwid.Padding(btxt, "center", "clip")

        m_select_comp = widget.CMSelectableListItem("Select Competition")

        m_details = widget.CMSelectableListItem("Current Competition")
        urwid.connect_signal(m_details, "click", self._on_screen_selected, CompetitionDetailsScreen)
        m_exit = widget.CMSelectableListItem("Exit")
        urwid.connect_signal(m_exit, "click", self._on_exit)

        menu = urwid.Pile([m_details, m_select_comp, urwid.Divider(), m_exit])

        view = urwid.Filler(
            urwid.Pile(
                [
                    hpad,
                    urwid.Padding(
                        urwid.LineBox(menu, "Main Menu", title_align="left"),
                        width=("relative", 80),
                        align="center",
                    ),
                ]
            ),
            "middle",
        )
        return view

    def _on_screen_selected(self, btn, screen_factory):
        asyncio.create_task(self._run_screen(screen_factory))

    def _on_exit(self, btn):
        self.response.set_result(None)

    async def _run_screen(self, screen_factory):
        screen = screen_factory(self.container)
        await screen.response
        self.container.original_widget = self.view

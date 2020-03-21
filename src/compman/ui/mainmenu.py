from typing import Callable, Optional
import urwid

import compman
from compman import storage
from compman.ui import widget
from compman.ui.activity import Activity


class MainMenuScreen(Activity):
    exithandler: Optional[Callable[[], None]] = None

    def show(self) -> None:
        super().show()

        if storage.get_settings().current_competition_id is None:
            self._run_screen("welcome")
        else:
            self._run_screen("details")

    def finish(self, result) -> None:
        super().finish(result)
        if self.exithandler is not None:
            self.exithandler()

    def on_exit(self, exithandler: Callable[[], None]) -> None:
        self.exithandler = exithandler

    def create_view(self):
        btxt = urwid.BigText("Compman", urwid.font.Thin6x6Font())
        hpad = urwid.Padding(urwid.AttrMap(btxt, "screen header"), urwid.CENTER, "clip")

        m_select_comp = widget.CMSelectableListItem("Select Competition")
        urwid.connect_signal(
            m_select_comp, "click", self._run_screen, user_args=["select"]
        )

        m_details = widget.CMSelectableListItem("Current Competition")
        urwid.connect_signal(
            m_details, "click", self._run_screen, user_args=["details"]
        )
        m_exit = widget.CMSelectableListItem("Exit")
        urwid.connect_signal(m_exit, "click", self._on_exit)

        menu = urwid.Pile([m_details, m_select_comp, urwid.Divider(), m_exit])

        view = urwid.Filler(
            urwid.Pile(
                [
                    hpad,
                    urwid.Text(self._get_version(), align=urwid.CENTER),
                    urwid.Padding(
                        urwid.LineBox(menu, "Main Menu", title_align="left"),
                        width=("relative", 80),
                        align=urwid.CENTER,
                    ),
                ]
            ),
            "middle",
        )
        return view

    def _on_exit(self, btn):
        self.finish(None)

    def _run_screen(self, screen_name, btn=None):
        # We want to import screen class as late as possible to avoid delays
        if screen_name == "welcome":
            from compman.ui.welcome import WelcomeScreen

            screen = WelcomeScreen(self.container)
        elif screen_name == "select":
            from compman.ui.selectcomp import SelectCompetitionScreen

            screen = SelectCompetitionScreen(self.container)
        else:
            assert screen_name == "details"
            from compman.ui.compdetails import CompetitionDetailsScreen

            screen = CompetitionDetailsScreen(self.container)
        screen.show()

    def _get_version(self) -> str:
        return f"Version {compman.__version__}"

import urwid

import compman
from compman import storage
from compman.ui import widget
from compman.ui.activity import Activity
from compman.ui.compdetails import CompetitionDetailsScreen
from compman.ui.selectcomp import SelectCompetitionScreen


class MainMenuScreen(Activity):
    def show(self) -> None:
        super().show()

        if storage.get_settings().current_competition_id is None:
            from compman.ui.welcome import WelcomeScreen

            self._run_screen(WelcomeScreen)
        else:
            self._run_screen(CompetitionDetailsScreen)

    def create_view(self):
        btxt = urwid.BigText("Compman", urwid.font.Thin6x6Font())
        hpad = urwid.Padding(urwid.AttrMap(btxt, "screen header"), urwid.CENTER, "clip")

        m_select_comp = widget.CMSelectableListItem("Select Competition")
        urwid.connect_signal(
            m_select_comp,
            "click",
            self._run_screen,
            user_args=[SelectCompetitionScreen],
        )

        m_details = widget.CMSelectableListItem("Current Competition")
        urwid.connect_signal(
            m_details, "click", self._run_screen, user_args=[CompetitionDetailsScreen]
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
        self.response.set_result(None)

    def _run_screen(self, screen_factory, btn=None):
        screen = screen_factory(self.container)
        screen.show()

    def _get_version(self) -> str:
        return f"Version {compman.__version__}"

import urwid

from compman.ui import widget
from compman.ui.activity import Activity
from compman.ui.compdetails import CompetitionDetailsScreen
from compman.ui.selectcomp import SelectCompetitionScreen


class MainMenuScreen(Activity):
    def create_view(self):
        btxt = urwid.BigText(u"Compman", urwid.font.Thin6x6Font())
        hpad = urwid.Padding(urwid.AttrMap(btxt, "screen header"), "center", "clip")

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

    def _on_exit(self, btn):
        self.response.set_result(None)

    def _run_screen(self, screen_factory, btn):
        screen = screen_factory(self.container)
        screen.show()

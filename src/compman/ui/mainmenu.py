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

        has_comps = storage.list_competitions()
        if not has_comps:
            return self._run_screen("welcome")

        curid = self._get_current_comp_id()
        if curid:
            return self._run_screen("details")

    def finish(self, result) -> None:
        super().finish(result)
        if self.exithandler is not None:
            self.exithandler()

    def on_exit(self, exithandler: Callable[[], None]) -> None:
        self.exithandler = exithandler

    def create_view(self):
        btxt = urwid.BigText("Compman", urwid.font.Thin6x6Font())
        hpad = urwid.Padding(urwid.AttrMap(btxt, "screen header"), urwid.CENTER, "clip")

        menuitems = []

        if self._get_current_comp_id():
            m_details = widget.CMSelectableListItem("Current Competition")
            urwid.connect_signal(
                m_details, "click", self._run_screen, user_args=["details"]
            )
            menuitems.append(m_details)

        m_select_comp = widget.CMSelectableListItem("Select Competition")
        urwid.connect_signal(
            m_select_comp, "click", self._run_screen, user_args=["select"]
        )
        menuitems.append(m_select_comp)

        menuitems.append(urwid.Divider())

        m_exit = widget.CMSelectableListItem("Exit")
        urwid.connect_signal(m_exit, "click", self._on_exit)
        menuitems.append(m_exit)

        menu = urwid.Pile(menuitems)

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
            coro = self._run_welcome()
        elif screen_name == "select":
            coro = self._run_select()
        else:
            assert screen_name == "details"
            coro = self._run_details()

        self.async_task(coro)

    async def _run_welcome(self) -> None:
        from compman.ui.welcome import WelcomeScreen

        screen = WelcomeScreen(self.container)
        screen.show()
        comp = await screen.response
        self.replace()
        if comp:
            self._run_screen("details")

    async def _run_select(self) -> None:
        from compman.ui.selectcomp import SelectCompetitionScreen

        screen = SelectCompetitionScreen(self.container)
        screen.show()
        comp = await screen.response
        self.replace()
        if comp:
            self._run_screen("details")

    async def _run_details(self) -> None:
        from compman.ui.compdetails import CompetitionDetailsScreen

        screen = CompetitionDetailsScreen(self.container)
        screen.show()
        await screen.response
        self.replace()

    def _get_version(self) -> str:
        return f"Version {compman.__version__}"

    def _get_current_comp_id(self) -> Optional[str]:
        curid = storage.get_settings().current_competition_id
        return curid if curid and storage.exists(curid) else None

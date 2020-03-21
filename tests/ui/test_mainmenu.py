import pytest

from compman import storage
from compman.ui.mainmenu import MainMenuScreen


@pytest.mark.asyncio
async def test_mainmenu_initial_welcome(storage_dir, activity_testbed) -> None:
    # View is opened with the welcome message
    welcome_screen = activity_testbed.mock("compman.ui.welcome.WelcomeScreen")
    async with activity_testbed.shown(MainMenuScreen):
        # THEN
        assert welcome_screen.shown


@pytest.mark.asyncio
async def test_mainmenu_details(storage_dir, activity_testbed) -> None:
    # GIVEN
    welcome_screen = activity_testbed.mock("compman.ui.welcome.WelcomeScreen")
    details_screen = activity_testbed.mock(
        "compman.ui.compdetails.CompetitionDetailsScreen"
    )
    async with activity_testbed.shown(MainMenuScreen):
        # WHEN
        assert welcome_screen.shown
        # Go back to main menu
        await activity_testbed.keypress("esc")

        contents = activity_testbed.render()
        assert "Current Competition" in contents

        focused = activity_testbed.get_focus_widgets()[-1]
        assert focused.get_label() == "Current Competition"
        await activity_testbed.keypress("enter")

        # THEN
        assert details_screen.shown


@pytest.mark.asyncio
async def test_mainmenu_select_comp(storage_dir, activity_testbed) -> None:
    welcome_screen = activity_testbed.mock("compman.ui.welcome.WelcomeScreen")
    select_screen = activity_testbed.mock(
        "compman.ui.selectcomp.SelectCompetitionScreen"
    )
    async with activity_testbed.shown(MainMenuScreen):
        # WHEN
        assert welcome_screen.shown
        # Go back to main menu
        await activity_testbed.keypress("esc")

        contents = activity_testbed.render()
        assert "Select Competition" in contents

        await activity_testbed.keypress("down")
        focused = activity_testbed.get_focus_widgets()[-1]
        assert focused.get_label() == "Select Competition"
        await activity_testbed.keypress("enter")

        # THEN
        assert select_screen.shown


@pytest.mark.asyncio
async def test_mainmenu_exit(storage_dir, activity_testbed) -> None:
    # GIVEN
    welcome_screen = activity_testbed.mock("compman.ui.welcome.WelcomeScreen")

    res = {"exited": False}

    def onexit():
        res["exited"] = True

    async with activity_testbed.shown(MainMenuScreen) as activity:
        activity.on_exit(onexit)

        # WHEN
        assert welcome_screen.shown
        # Go back to main menu
        await activity_testbed.keypress("esc")

        # THEN
        contents = activity_testbed.render()
        assert "Exit" in contents

        await activity_testbed.keypress("down")
        await activity_testbed.keypress("down")
        focused = activity_testbed.get_focus_widgets()[-1]
        assert focused.get_label() == "Exit"
        await activity_testbed.keypress("enter")

        # THEN
        assert res["exited"] == True


@pytest.mark.asyncio
async def test_mainmenu_details_if_comp_selected(storage_dir, activity_testbed) -> None:
    # GIVEN
    welcome_screen = activity_testbed.mock("compman.ui.welcome.WelcomeScreen")
    details_screen = activity_testbed.mock(
        "compman.ui.compdetails.CompetitionDetailsScreen"
    )
    storage.get_settings().current_competition_id = "test"
    storage.save_settings()
    async with activity_testbed.shown(MainMenuScreen):
        # THEN
        assert not welcome_screen.shown
        assert details_screen.shown

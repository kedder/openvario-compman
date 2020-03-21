import pytest

from compman import storage
from compman.ui.welcome import WelcomeScreen


@pytest.mark.asyncio
async def test_welcomescreen_view(activity_testbed) -> None:
    # View is opened with the welcome message
    async with activity_testbed.shown(WelcomeScreen):
        # WHEN
        contents = activity_testbed.render()

        # THEN
        assert "Welcome to Competition Manager" in contents
        assert "Set Up a Competition" in contents


@pytest.mark.asyncio
async def test_welcomescreen_setup_comp(
    storage_dir, soaringspot, activity_testbed
) -> None:
    # User picks a competition and end up in competition details screen
    # GIVEN
    sspicker_screen = activity_testbed.mock(
        "compman.ui.soaringspot.SoaringSpotPickerScreen"
    )
    sspicker_screen.result = storage.StoredCompetition(
        id="test", title="Test", soaringspot_url="http://test"
    )
    details_screen = activity_testbed.mock(
        "compman.ui.compdetails.CompetitionDetailsScreen"
    )

    async with activity_testbed.shown(WelcomeScreen):
        # WHEN
        await activity_testbed.keypress("enter")

        # THEN
        assert sspicker_screen.shown
        assert details_screen.shown
        assert storage.get_settings().current_competition_id == "test"


@pytest.mark.asyncio
async def test_welcomescreen_setup_cancelled(soaringspot, activity_testbed) -> None:
    # User chooses to set up the competition but presses escape and gets back
    # to welcome screen.
    sspicker_screen = activity_testbed.mock(
        "compman.ui.soaringspot.SoaringSpotPickerScreen"
    )
    details_screen = activity_testbed.mock(
        "compman.ui.compdetails.CompetitionDetailsScreen"
    )

    async with activity_testbed.shown(WelcomeScreen):
        # WHEN
        await activity_testbed.keypress("enter")
        await activity_testbed.keypress("esc")

        # THEN
        assert sspicker_screen.shown
        assert not details_screen.shown

        contents = activity_testbed.render()
        assert "Welcome to Competition Manager" in contents
        assert "Set Up a Competition" in contents

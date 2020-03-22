import pytest

from compman import storage
from compman.ui.selectcomp import SelectCompetitionScreen


@pytest.mark.asyncio
async def test_selectcomp_view_initial(storage_dir, activity_testbed) -> None:
    async with activity_testbed.shown(SelectCompetitionScreen):
        content = activity_testbed.render()
        assert "Switch competition" in content
        focus = activity_testbed.get_focus_widgets()[-1]
        assert "New competition" in focus.get_label()


@pytest.mark.asyncio
async def test_selectcomp_view_existing(storage_dir, activity_testbed) -> None:
    # GIVEN

    details_screen = activity_testbed.mock(
        "compman.ui.compdetails.CompetitionDetailsScreen"
    )

    storage.save_competition(storage.StoredCompetition("one", title="One"))
    storage.save_competition(storage.StoredCompetition("two", title="Two"))

    # WHEN
    async with activity_testbed.shown(SelectCompetitionScreen):
        content = activity_testbed.render()

        assert "One" in content
        assert "Two" in content
        focus = activity_testbed.get_focus_widgets()[-1]
        assert focus.get_label() == "One"

        await activity_testbed.keypress("enter")

        # THEN
        assert details_screen.shown

        settings = storage.get_settings()
        assert settings.current_competition_id == "one"


@pytest.mark.asyncio
async def test_selectcomp_new_comp_cancel(storage_dir, activity_testbed) -> None:
    sspicker_screen = activity_testbed.mock(
        "compman.ui.soaringspot.SoaringSpotPickerScreen"
    )

    async with activity_testbed.shown(SelectCompetitionScreen):
        content = activity_testbed.render()
        assert "Switch competition" in content
        focus = activity_testbed.get_focus_widgets()[-1]
        assert "New competition" in focus.get_label()
        await activity_testbed.keypress("enter")
        await activity_testbed.keypress("esc")

        assert sspicker_screen.shown
        content = activity_testbed.render()
        assert "Switch competition" in content


@pytest.mark.asyncio
async def test_selectcomp_new_comp_select(storage_dir, activity_testbed) -> None:
    sspicker_screen = activity_testbed.mock(
        "compman.ui.soaringspot.SoaringSpotPickerScreen"
    )
    sspicker_screen.result = storage.StoredCompetition("one", title="One")

    details_screen = activity_testbed.mock(
        "compman.ui.compdetails.CompetitionDetailsScreen"
    )

    async with activity_testbed.shown(SelectCompetitionScreen):
        focus = activity_testbed.get_focus_widgets()[-1]
        assert "New competition" in focus.get_label()
        await activity_testbed.keypress("enter")

        assert sspicker_screen.shown
        assert details_screen.shown

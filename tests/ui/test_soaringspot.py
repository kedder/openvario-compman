import asyncio

import pytest

from compman.ui.soaringspot import SoaringSpotPickerScreen
from compman.soaringspot import SoaringSpotContest
from compman import storage

from tests.fixtures.soaringspot import SoaringSpotFixture
from tests.fixtures.activitytestbed import ActivityTestbed


@pytest.mark.asyncio
async def test_soaringspot_no_contests(
    soaringspot: SoaringSpotFixture, activity_testbed: ActivityTestbed
) -> None:
    async with activity_testbed.shown(SoaringSpotPickerScreen):
        contents = activity_testbed.render()
        assert "Pick a new competition" in contents


@pytest.mark.asyncio
async def test_soaringspot_view(
    soaringspot: SoaringSpotFixture, activity_testbed: ActivityTestbed
) -> None:

    soaringspot.competitions = [
        SoaringSpotContest(
            id="one",
            href="http://soaringspot.local/one",
            title="One",
            description="First contest",
        ),
        SoaringSpotContest(
            id="two",
            href="http://soaringspot.local/two",
            title="Two",
            description="Second contest",
        ),
    ]

    async with activity_testbed.shown(SoaringSpotPickerScreen):
        contents = activity_testbed.render()
        assert "Pick a new competition" in contents

        await activity_testbed.gather_tasks()
        contents = activity_testbed.render()
        assert "One" in contents
        assert "Two" in contents

        focused = activity_testbed.get_focus_widgets()[-1]
        assert focused.get_label() == "One"


@pytest.mark.asyncio
async def test_soaringspot_select(
    storage_dir: str, soaringspot: SoaringSpotFixture, activity_testbed: ActivityTestbed
) -> None:
    # GIVEN
    soaringspot.competitions = [
        SoaringSpotContest(
            id="one",
            href="http://soaringspot.local/one",
            title="One",
            description="First contest",
        ),
        SoaringSpotContest(
            id="two",
            href="http://soaringspot.local/two",
            title="Two",
            description="Second contest",
        ),
    ]

    # WHEN
    async with activity_testbed.shown(SoaringSpotPickerScreen):
        await activity_testbed.gather_tasks()
        await activity_testbed.keypress("down")
        focused = activity_testbed.get_focus_widgets()[-1]
        assert focused.get_label() == "Two"
        assert "Second contest" in activity_testbed.render()

        await activity_testbed.keypress("enter")

        # THEN
        res = await activity_testbed.response()
        assert isinstance(res, storage.StoredCompetition)
        assert res.id == "two"
        assert res.title == "Two"
        assert res.soaringspot_url == "http://soaringspot.local/two"


@pytest.mark.asyncio
async def test_soaringspot_existing(
    storage_dir: str, soaringspot: SoaringSpotFixture, activity_testbed: ActivityTestbed
) -> None:
    # GIVEN
    storage.save_competition(storage.StoredCompetition(id="one", title="One"))

    soaringspot.competitions = [
        SoaringSpotContest(
            id="one",
            href="http://soaringspot.local/one",
            title="One",
            description="First contest",
        ),
        SoaringSpotContest(
            id="two",
            href="http://soaringspot.local/two",
            title="Two",
            description="Second contest",
        ),
    ]

    # WHEN
    async with activity_testbed.shown(SoaringSpotPickerScreen):
        await activity_testbed.gather_tasks()
        focused = activity_testbed.get_focus_widgets()[-1]
        assert focused.get_label() == "One"
        assert "First contest" in activity_testbed.render()
        await activity_testbed.keypress("enter")

        # THEN
        res = await activity_testbed.response()
        assert isinstance(res, storage.StoredCompetition)
        assert res.id == "one"
        assert res.title == "One"
        assert res.soaringspot_url == "http://soaringspot.local/one"

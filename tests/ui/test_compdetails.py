import asyncio

import pytest

from compman import storage, xcsoar
from compman.soaringspot import DownloadableFileType, SoaringSpotDownloadableFile
from compman.soarscore import SoarScoreTaskInfo
from compman.ui.compdetails import CompetitionDetailsScreen


@pytest.mark.asyncio
async def test_compdetails_view(
    storage_dir, soaringspot, soarscore, xcsoar_dir, activity_testbed
) -> None:
    # GIVEN
    _setup_test_comp()
    async with activity_testbed.shown(CompetitionDetailsScreen):
        assert "Test Competition" in activity_testbed.render()
        await asyncio.sleep(0)
        assert "Refreshing file list..." in activity_testbed.render()
        await asyncio.sleep(0)
        assert "No updates" in activity_testbed.render()


@pytest.mark.asyncio
async def test_compdetails_download(
    storage_dir, soaringspot, soarscore, xcsoar_dir, activity_testbed
) -> None:
    # GIVEN
    comp = _setup_test_comp()
    soaringspot.files = [
        SoaringSpotDownloadableFile(
            "airspace.txt",
            href=f"{comp.soaringspot_url}/airspace.txt",
            kind=DownloadableFileType.AIRSPACE,
        )
    ]
    soaringspot.file_contents = b"Hello World!"

    # WHEN
    async with activity_testbed.shown(CompetitionDetailsScreen):
        await asyncio.sleep(0)
        assert "Refreshing file list..." in activity_testbed.render()
        await asyncio.sleep(0)
        assert "New contest files detected!" in activity_testbed.render()
        assert "airspace.txt" in activity_testbed.render()
        await asyncio.sleep(0)

        assert "Downloading..." in activity_testbed.render()
        await asyncio.sleep(0)
        assert "New!" in activity_testbed.render()
        assert "airspace.txt (12.0B)" in activity_testbed.render()
        await asyncio.sleep(0)


@pytest.mark.asyncio
async def test_compdetails_activate(
    storage_dir, soaringspot, soarscore, activity_testbed, xcsoar_dir, async_sleep
) -> None:
    # GIVEN
    comp = _setup_test_comp()
    soaringspot.files = [
        SoaringSpotDownloadableFile(
            "airspace.txt",
            href=f"{comp.soaringspot_url}/airspace.txt",
            kind=DownloadableFileType.AIRSPACE,
        ),
        SoaringSpotDownloadableFile(
            "waypoints.cup",
            href=f"{comp.soaringspot_url}/waypoints.cup",
            kind=DownloadableFileType.WAYPOINT,
        ),
    ]
    soaringspot.file_contents = b"Hello World!"

    async with activity_testbed.shown(CompetitionDetailsScreen):
        # Let everything to be downloaded
        await activity_testbed.gather_tasks()

        assert "New contest files detected!" in activity_testbed.render()

        await activity_testbed.keypress("enter", "down")
        focused = activity_testbed.get_focus_widgets()[-1]
        assert focused.get_label() == "Activate"
        await activity_testbed.keypress("enter")

        # THEN
        assert "XCSoar profiles updated" in activity_testbed.render()


@pytest.mark.asyncio
async def test_compdetails_select_files(
    storage_dir, soaringspot, soarscore, activity_testbed, xcsoar_dir, async_sleep
) -> None:
    # GIVEN
    comp = _setup_test_comp()
    soaringspot.files = [
        SoaringSpotDownloadableFile(
            "airspace.txt",
            href=f"{comp.soaringspot_url}/airspace.txt",
            kind=DownloadableFileType.AIRSPACE,
        ),
        SoaringSpotDownloadableFile(
            "waypoints.cup",
            href=f"{comp.soaringspot_url}/waypoints.cup",
            kind=DownloadableFileType.WAYPOINT,
        ),
    ]
    soaringspot.file_contents = b"Hello World!"

    # WHEN
    async with activity_testbed.shown(CompetitionDetailsScreen):
        # Let everything to be downloaded
        await activity_testbed.gather_tasks()

        assert "New contest files detected!" in activity_testbed.render()

        # Now select profile, airspace and waypoint files
        await activity_testbed.keypress("enter", "up", "enter", "up", "enter")

        # THEN
        content = activity_testbed.render()
        assert "(X) airspace.txt" in content
        assert "(X) waypoints.cup" in content
        assert "Airspace changed to: airspace.txt" in content
        assert "[X] openvario.prf" in content

    with open(xcsoar.get_xcsoar_profile_filename("openvario.prf"), "r") as f:
        profile_contents = f.read()

    assert "waypoints.cup" in profile_contents
    assert "airspace.txt" in profile_contents


@pytest.mark.asyncio
async def test_compdetails_select_class_and_download_task(
    storage_dir, soaringspot, soarscore, activity_testbed, xcsoar_dir, async_sleep
) -> None:
    _setup_test_comp()
    soaringspot.classes = ["Club", "Standard"]
    soarscore.tasks = [
        SoarScoreTaskInfo(
            comp_class="Club",
            title="Club Task",
            day_no=1,
            task_no=1,
            timestamp="now",
            task_url="http://soarscore.com/club.tsk",
        ),
        SoarScoreTaskInfo(
            comp_class="Standard",
            title="Standard Task",
            day_no=1,
            task_no=1,
            timestamp="now",
            task_url="http://soarscore.com/standard.tsk",
        ),
    ]

    async with activity_testbed.shown(CompetitionDetailsScreen):
        # Let everything to be downloaded
        await activity_testbed.gather_tasks()
        rendered = activity_testbed.render()
        assert "Select competition class to download task" in rendered
        assert "Pick your competition class" in rendered

        # Pick "Standard"
        await activity_testbed.keypress("up", "enter")
        rendered = activity_testbed.render()
        assert "Competition class" in rendered
        assert "Standard" in rendered
        await activity_testbed.gather_tasks()

        # Make sure we see the Standard class task
        rendered = activity_testbed.render()
        assert "Today's task" in rendered
        assert "Standard Task day 1 task 1" in rendered

        # Click download
        await activity_testbed.keypress("down", "enter")
        await asyncio.sleep(0)
        assert "Downloading Standard Task..." in activity_testbed.render()
        await asyncio.sleep(0)
        # await activity_testbed.gather_tasks()
        rendered = activity_testbed.render()
        assert "Task downloaded and installed" in rendered


def _setup_test_comp() -> storage.StoredCompetition:
    comp = storage.StoredCompetition(
        id="test",
        title="Test Competition",
        soaringspot_url="https://soaringspot.local/test",
    )
    storage.save_competition(comp, set_current=True)
    return comp

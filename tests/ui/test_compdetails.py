import asyncio

import pytest

from compman import storage
from compman import xcsoar
from compman.soaringspot import SoaringSpotDownloadableFile, DownloadableFileType
from compman.ui.compdetails import CompetitionDetailsScreen


@pytest.mark.asyncio
async def test_compdetails_view(
    storage_dir, soaringspot, xcsoar_dir, activity_testbed
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
    storage_dir, soaringspot, xcsoar_dir, activity_testbed
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
    storage_dir, soaringspot, activity_testbed, xcsoar_dir, async_sleep
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
    storage_dir, soaringspot, activity_testbed, xcsoar_dir, async_sleep
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


def _setup_test_comp() -> storage.StoredCompetition:
    comp = storage.StoredCompetition(
        id="test",
        title="Test Competition",
        soaringspot_url="https://soaringspot.local/test",
    )
    storage.save_competition(comp, set_current=True)
    return comp

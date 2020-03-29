import pytest

from compman import soaringspot


@pytest.mark.asyncio
async def test_fetch_competitions() -> None:
    # WHEN
    comps = await soaringspot.fetch_competitions()

    # THEN
    # list of competitions changes all the time, so all we can assert is that
    # list is not empty.

    assert len(comps) > 0


@pytest.mark.asyncio
async def test_fetch_downloads() -> None:
    # GIVEN
    ssurl = "https://www.soaringspot.com/en_gb/wgc2018pl/"

    # WHEN
    downloads = await soaringspot.fetch_downloads(ssurl)

    # THEN
    assert len(downloads) == 2

    dl0 = downloads[0]
    assert dl0.filename == "wgc2018_airspace_v5.1_openair.txt"
    assert dl0.kind == soaringspot.DownloadableFileType.AIRSPACE

    dl1 = downloads[1]
    assert dl1.filename == "pz_wgc_2018_v1.2.cup"
    assert dl1.kind == soaringspot.DownloadableFileType.WAYPOINT


@pytest.mark.asyncio
async def test_fetch_file() -> None:
    # GIVEN
    ssurl = "https://www.soaringspot.com/en_gb/wgc2018pl/"
    downloads = await soaringspot.fetch_downloads(ssurl)
    dl0 = downloads[0]

    # WHEN
    fetched = await soaringspot.fetch_file(dl0.href)
    content = fetched.read()

    # THEN
    assert len(content) == 138067

import os
import shutil
import asyncio

import pytest

from compman import storage
from compman import xcsoar
from .fixtures.soaringspot import SoaringSpotFixture
from .fixtures.activitytestbed import ActivityTestbed

HERE = os.path.dirname(__file__)


@pytest.fixture()
def soaringspot():
    ssf = SoaringSpotFixture()
    ssf.setUp()
    try:
        yield ssf
    finally:
        ssf.tearDown()


@pytest.fixture
def storage_dir(tmpdir):
    storage.init(tmpdir)
    yield tmpdir
    storage.deinit()


@pytest.fixture
def activity_testbed(mocker):
    yield ActivityTestbed(mocker)


@pytest.fixture
def xcsoar_dir(tmpdir):
    xcsoar_sample_dir = os.path.join(HERE, "fixtures", "xcsoar")
    xcsoardir = os.path.join(tmpdir, ".xcsoar")
    shutil.copytree(xcsoar_sample_dir, xcsoardir)
    xcsoar.init(xcsoardir)
    yield xcsoardir
    xcsoar.deinit()


@pytest.fixture
def async_sleep(mocker):
    realsleep = asyncio.sleep

    async def sleep_mock(time: float) -> None:
        await realsleep(0)

    mocker.patch("asyncio.sleep", sleep_mock)

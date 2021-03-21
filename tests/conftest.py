import asyncio
import os
import shutil

import pytest

from compman import storage, xcsoar

from .fixtures.activitytestbed import ActivityTestbed
from .fixtures.soaringspot import SoaringSpotFixture
from .fixtures.soarscore import SoarScoreFixture
from .fixtures.widgettestbed import WidgetTestbedFactory

HERE = os.path.dirname(__file__)


@pytest.fixture()
def soaringspot():
    ssf = SoaringSpotFixture()
    ssf.setUp()
    try:
        yield ssf
    finally:
        ssf.tearDown()


@pytest.fixture()
def soarscore():
    ssf = SoarScoreFixture()
    ssf.setUp()
    try:
        yield ssf
    finally:
        ssf.tearDown()


@pytest.fixture
def storage_dir(tmpdir):
    storage.init(tmpdir)
    try:
        yield tmpdir
    finally:
        storage.deinit()


@pytest.fixture
def sample_competition(storage_dir):
    comp = storage.StoredCompetition("test", "Test competition")
    storage.save_competition(comp)
    settings = storage.get_settings()
    settings.current_competition_id = comp.id
    storage.save_settings()
    try:
        yield comp
    finally:
        settings.current_competition_id = None
        storage.save_settings()
        storage.delete_competition(comp.id)


@pytest.fixture
def widget_testbed():
    yield WidgetTestbedFactory()


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

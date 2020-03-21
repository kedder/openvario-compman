import pytest

from compman import storage
from .fixtures.soaringspot import SoaringSpotFixture
from .fixtures.activitytestbed import ActivityTestbed


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

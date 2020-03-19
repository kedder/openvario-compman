import pytest

from compman import storage
from .fixtures.soaringspot import SoaringSpotFixture


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

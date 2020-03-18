import pytest

from .fixtures.soaringspot import SoaringSpotFixture


@pytest.fixture()
def soaringspot():
    ssf = SoaringSpotFixture()
    ssf.setUp()
    try:
        yield ssf
    finally:
        ssf.tearDown()

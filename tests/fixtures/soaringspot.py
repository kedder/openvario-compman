from typing import List, IO, Optional
from unittest import mock
import io
import asyncio


from compman.soaringspot import SoaringSpotContest, SoaringSpotDownloadableFile


class SoaringSpotFixture:
    classes: List[str]
    competitons: List[SoaringSpotContest]
    files: List[SoaringSpotDownloadableFile]
    file_contents: bytes

    fetch_clases_exc: Optional[Exception] = None
    fetch_competitions_exc: Optional[Exception] = None
    fetch_downloads_exc: Optional[Exception] = None

    def setUp(self) -> None:
        self.reset()

        self._patches: List[mock._patch] = [
            mock.patch(
                "compman.soaringspot.fetch_competitions", self.fetch_competitions_mock
            ),
            mock.patch("compman.soaringspot.fetch_classes", self.fetch_classes_mock),
            mock.patch(
                "compman.soaringspot.fetch_downloads", self.fetch_downloads_mock
            ),
            mock.patch("compman.http.fetch_file", self.fetch_file_mock),
        ]

        for p in self._patches:
            p.start()

    def tearDown(self) -> None:
        for p in self._patches:
            p.stop()

    def reset(self):
        self.classes = []
        self.competitions = []
        self.files = []
        self.file_contents = b""

    async def fetch_competitions_mock(self) -> List[SoaringSpotContest]:
        # Downloading...
        await asyncio.sleep(0)
        if self.fetch_competitions_exc is not None:
            raise self.fetch_competitions_exc
        return self.competitions

    async def fetch_classes_mock(self, comp_url: str) -> List[str]:
        # Downloading...
        await asyncio.sleep(0)
        if self.fetch_clases_exc is not None:
            raise self.fetch_clases_exc
        return self.classes

    async def fetch_downloads_mock(
        self, comp_url: str
    ) -> List[SoaringSpotDownloadableFile]:
        # Downloading...
        await asyncio.sleep(0)
        if self.fetch_downloads_exc is not None:
            raise self.fetch_downloads_exc
        return self.files

    async def fetch_file_mock(self, file_url: str) -> IO[bytes]:
        # Downloading...
        await asyncio.sleep(0)
        return io.BytesIO(self.file_contents)

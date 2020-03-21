from typing import List, IO
from unittest import mock
import io
import asyncio


from compman.soaringspot import SoaringSpotContest, SoaringSpotDownloadableFile


class SoaringSpotFixture:
    competitons: List[SoaringSpotContest]
    files: List[SoaringSpotDownloadableFile]
    file_contents: bytes

    def setUp(self) -> None:
        self.reset()

        self._patches = [
            mock.patch(
                "compman.soaringspot.fetch_competitions", self.fetch_competitions_mock
            ),
            mock.patch(
                "compman.soaringspot.fetch_downloads", self.fetch_downloads_mock
            ),
            mock.patch("compman.soaringspot.fetch_file", self.fetch_file_mock),
        ]

        for p in self._patches:
            p.start()

    def tearDown(self) -> None:
        for p in self._patches:
            p.stop()

    def reset(self):
        self.competitions = []
        self.files = []
        self.file_contents = b""

    async def fetch_competitions_mock(self) -> List[SoaringSpotContest]:
        # Downloading...
        await asyncio.sleep(0)
        return self.competitions

    async def fetch_downloads_mock(
        self, comp_url: str
    ) -> List[SoaringSpotDownloadableFile]:
        # Downloading...
        await asyncio.sleep(0)
        return self.files

    async def fetch_file_mock(self, file_url: str) -> IO[bytes]:
        # Downloading...
        await asyncio.sleep(0)
        return io.BytesIO(self.file_contents)

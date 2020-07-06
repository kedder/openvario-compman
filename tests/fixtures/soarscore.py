from typing import List, Optional
import asyncio

import mock

from compman.soarscore import SoarScoreTaskInfo


class SoarScoreFixture:
    tasks: List[SoarScoreTaskInfo]
    task_content = b""
    fetch_latest_tasks_exc: Optional[Exception] = None

    def setUp(self) -> None:
        self.reset()

        self._patches = [
            mock.patch("compman.soarscore.fetch_latest_tasks", self.fetch_latest_tasks),
            mock.patch("compman.soarscore.fetch_url", self.fetch_url),
        ]

        for p in self._patches:
            p.start()

    def tearDown(self) -> None:
        for p in self._patches:
            p.stop()

    def reset(self):
        self.tasks = []

    async def fetch_latest_tasks(self, comp_id: str) -> List[SoarScoreTaskInfo]:
        # Downloading...
        await asyncio.sleep(0)
        if self.fetch_latest_tasks_exc is not None:
            raise self.fetch_latest_tasks_exc
        return self.tasks

    async def fetch_url(self, url: str) -> bytes:
        # Downloading...
        await asyncio.sleep(0)
        return self.task_content

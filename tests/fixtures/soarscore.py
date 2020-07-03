from typing import List
import asyncio

import mock

from compman.soarscore import SoarScoreTaskInfo


class SoarScoreFixture:
    tasks: List[SoarScoreTaskInfo]

    def setUp(self) -> None:
        self.reset()

        self._patches = [
            mock.patch("compman.soarscore.fetch_latest_tasks", self.fetch_latest_tasks),
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
        return self.tasks

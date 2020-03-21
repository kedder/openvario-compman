from typing import Optional, Type
import asyncio
from contextlib import asynccontextmanager

import urwid

from compman.ui.activity import Activity


class ActivityStub(Activity):
    _result: Optional[object] = None

    def __init__(
        self, container, monitor: "ActivityStubMonitor", result: Optional[object]
    ) -> None:
        super().__init__(container)
        self._monitor = monitor
        self._result = result
        self._monitor.created = True

    def create_view(self) -> None:
        return urwid.SolidFill("T")

    def show(self) -> None:
        super().show()
        self._monitor.shown = True
        if self._result is not None:
            self.finish(self._result)


class ActivityStubMonitor:
    def __init__(self, result: object = None) -> None:
        self.result = result
        self.created = False
        self.shown = False

    def create(self, container):
        return ActivityStub(container, self, self.result)


class ActivityTestbed:
    def __init__(self, mocker) -> None:
        self.mocker = mocker
        self.container = urwid.WidgetPlaceholder(urwid.SolidFill("T"))
        self.activity: Optional[Activity] = None

    @asynccontextmanager
    async def shown(self, act_factory: Type[Activity]):
        self.activity = act_factory(self.container)
        self.activity.show()

        yield self.activity

        if not self.activity.is_finished():
            self.activity.finish(None)
        await asyncio.wait_for(asyncio.gather(*self.activity._tasks), 1)
        self.activity = None

    def mock(self, spec, result: object = None) -> ActivityStubMonitor:
        monitor = ActivityStubMonitor(result)
        self.mocker.patch(spec, monitor.create)
        return monitor

    def render(self, size=(60, 40)):
        canvas = self.container.render(size)
        contents = [t.decode("utf-8") for t in canvas.text]
        return "\n".join(contents)

    async def keypress(self, key: str) -> Optional[str]:
        res = self.container.keypress((0, 0), key)
        await asyncio.sleep(0)
        return res

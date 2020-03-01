import asyncio
import logging

import urwid

from compman.ui import widget

log = logging.getLogger("compman")


class Activity:
    def __init__(self, container):
        self.container = container
        self.response = asyncio.Future()

    def show(self):
        self._tasks = []
        self._previous_widget = self.container.original_widget
        self.container.original_widget = widget.CMGlobalCommands(
            self.create_view(), self
        )

    def finish(self, result):
        # Cancel any outstanding tasks
        for t in self._tasks:
            t.cancel()

        self.container.original_widget = self._previous_widget
        self.response.set_result(result)

    def create_view(self) -> urwid.Widget:
        raise NotImplementedError()

    def connect_async(self, widget, signal, handler_coro, user_args=None):
        urwid.connect_signal(
            widget,
            signal,
            self._async_handler,
            user_args=[handler_coro, user_args or []],
        )

    def _async_handler(self, handler_coro, args, widget):
        task = asyncio.create_task(self._logged_exceptions(handler_coro(*args)))
        self._tasks.append(task)

    def async_task(self, coro):
        log.info("Starting task {coro}")
        task = asyncio.create_task(self._logged_exceptions(coro))
        self._tasks.append(task)

    async def run_activity(self, act: "Activity"):
        log.info(f"Running activity {act.__class__}")
        act.show()
        resp = await act.response
        log.info(f"Activity {act.__class__} completed with {resp}")
        return resp

    async def _logged_exceptions(self, coro):
        try:
            return await coro
        except Exception:
            log.exception("Exception in activity async task")
            raise

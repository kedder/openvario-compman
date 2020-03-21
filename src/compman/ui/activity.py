from typing import Set
import asyncio
import logging

import urwid

from compman.ui import widget

log = logging.getLogger("compman")


class Activity:
    _previous_widget: urwid.Widget = None
    _tasks: Set[asyncio.Task]

    def __init__(self, container):
        self.container = container
        self.response = asyncio.Future()

    def create_view(self) -> urwid.Widget:
        raise NotImplementedError()

    def show(self) -> None:
        self._tasks = set()
        self._previous_widget = self.container.original_widget
        self.container.original_widget = widget.CMGlobalCommands(
            self.create_view(), self
        )

    def finish(self, result):
        if self._previous_widget is None:
            raise RuntimeError("Activity is not started or already finished")
        # Cancel any outstanding tasks on a next event loop iteration to avoid
        # cancelling the task that calls finish() right now.
        asyncio.get_running_loop().call_soon(self._cancel_outstanding_tasks)

        # Restore the prvious UI
        self.container.original_widget = self._previous_widget
        self._previous_widget = None

        self.response.set_result(result)

    def is_finished(self) -> bool:
        return self._previous_widget is None

    def connect_async(self, widget, signal, handler_coro, user_args=None):
        urwid.connect_signal(
            widget,
            signal,
            self._async_handler,
            user_args=[handler_coro, user_args or []],
        )

    async def run_activity(self, act: "Activity"):
        log.debug(f"Running activity {act.__class__}")
        act.show()
        resp = await act.response
        log.debug(f"Activity {act.__class__} completed with {resp}")
        return resp

    def async_task(self, coro):
        task = asyncio.create_task(coro)
        log.debug(f"Started {task}")
        task.add_done_callback(self._task_done)
        self._tasks.add(task)
        return task

    def _async_handler(self, handler_coro, args, widget):
        coro = handler_coro(*args)
        return self.async_task(coro)

    def _cancel_outstanding_tasks(self):
        # Cancel any outstanding tasks
        notdone = [t for t in self._tasks if not t.done()]
        if notdone:
            log.info(
                f"Cancelling {len(notdone)} outstanding tasks "
                f"for {self.__class__.__name__}"
            )
        for t in notdone:
            t.cancel()

    def _task_done(self, task):
        self._tasks.remove(task)
        if task.cancelled():
            log.debug(f"Cancelled: {task}")
            return
        exc = task.exception()
        if exc is not None:
            log.error(f"Failed: {task}", exc_info=exc)
        else:
            log.debug(f"Completed: {task}")

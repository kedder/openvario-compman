from typing import List, Optional

import urwid

from compman import soarscore, storage
from compman.ui import widget
from compman.ui.activity import Activity


class TaskDownloadWidget(urwid.WidgetWrap):
    signals = ["download"]

    def __init__(self, activity: Activity, comp: storage.StoredCompetition) -> None:
        self._activity = activity
        self._comp = comp
        self._tasks: List[soarscore.SoarScoreTaskInfo] = []

        self._activity.async_task(self._fetch_tasks())
        super().__init__(urwid.Pile([]))

    def refresh(self) -> None:
        self._activity.async_task(self._fetch_tasks())

    async def _fetch_tasks(self) -> None:
        if self._comp.soaringspot_url is None:
            return

        self._w = urwid.Text(("progress", "Fetching today's task..."))

        try:
            self._tasks = await soarscore.fetch_latest_tasks(self._comp.id)
        except soarscore.SoarScoreClientError as e:
            self._w = urwid.Text(("error message", f"Error fetching today's task: {e}"))
            return

        self._create_task_view()

    def _get_task(self) -> Optional[soarscore.SoarScoreTaskInfo]:
        for ti in self._tasks:
            if ti.comp_class == self._comp.selected_class:
                return ti
        return None

    def _create_task_view(self) -> None:
        if self._comp.selected_class is None:
            self._w = urwid.Text(
                ("remark", "Select competition class to download task")
            )
            return

        refresh_btn = widget.CMButton(" Refresh ")
        urwid.connect_signal(refresh_btn, "click", self._on_refresh)

        curtask = self._get_task()
        if curtask is None:
            self._w = urwid.Columns(
                [
                    ("pack", urwid.Text(("remark", "No task for today"))),
                    ("pack", refresh_btn),
                ],
                dividechars=1,
            )
            return

        task_title = urwid.Text(
            [
                ("highlight", curtask.title),
                " day ",
                ("highlight", str(curtask.day_no)),
                " task ",
                ("highlight", str(curtask.task_no)),
            ]
        )
        task_timestamp = urwid.Text(["Generated on ", curtask.timestamp])

        self.download_btn = widget.CMButton("Download")
        urwid.connect_signal(self.download_btn, "click", self._on_download, curtask)

        self._w = urwid.Pile(
            [
                urwid.Text("Today's task"),
                urwid.Padding(task_title, left=2),
                urwid.Padding(task_timestamp, left=2),
                urwid.Divider(),
                widget.ButtonRow([self.download_btn, refresh_btn]),
            ]
        )

    def _on_refresh(self, btn):
        self._activity.async_task(self._fetch_tasks())

    def _on_download(self, btn, taskinfo: soarscore.SoarScoreTaskInfo):
        self._emit("download", taskinfo)

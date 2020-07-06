import asyncio

import pytest
import urwid

from compman.ui.activity import Activity
from compman.ui.taskdownload import TaskDownloadWidget
from compman import storage
from compman.soarscore import SoarScoreClientError, SoarScoreTaskInfo


class ActivityStub(Activity):
    async def wait_for_tasks(self) -> None:
        await asyncio.wait(self._tasks)


@pytest.mark.asyncio
async def test_taskdownload_noclasses(storage_dir, soarscore, widget_testbed) -> None:
    comp = storage.StoredCompetition(
        "test", "Test Competition", soaringspot_url="http://soaringspot.com/test"
    )
    act = ActivityStub(urwid.SolidFill("T"))
    wdg = TaskDownloadWidget(act, comp)
    wtb = widget_testbed.for_widget(wdg)

    # await act.wait_for_tasks()
    await asyncio.sleep(0)
    assert "Fetching today's task..." in wtb.render()

    # When classes are not known, we cannot pick task
    await act.wait_for_tasks()
    assert "Select competition class to download task" in wtb.render()


@pytest.mark.asyncio
async def test_taskdownload_notask(storage_dir, soarscore, widget_testbed) -> None:
    comp = storage.StoredCompetition(
        "test",
        "Test Competition",
        soaringspot_url="http://soaringspot.com/test",
        selected_class="Club",
    )
    act = ActivityStub(urwid.SolidFill("T"))
    wdg = TaskDownloadWidget(act, comp)
    wtb = widget_testbed.for_widget(wdg)
    await act.wait_for_tasks()

    rendered = wtb.render()
    assert "No task for today" in rendered
    assert "Refresh" in rendered


@pytest.mark.asyncio
async def test_taskdownload_task_view(storage_dir, soarscore, widget_testbed) -> None:
    comp = storage.StoredCompetition(
        "test",
        "Test Competition",
        soaringspot_url="http://soaringspot.com/test",
        selected_class="Club",
    )
    act = ActivityStub(urwid.SolidFill("T"))
    wdg = TaskDownloadWidget(act, comp)
    wtb = widget_testbed.for_widget(wdg)
    soarscore.tasks = [
        SoarScoreTaskInfo(
            comp_class="Club",
            title="Club Task",
            day_no=1,
            task_no=1,
            timestamp="now",
            task_url="http://soarscore.com/club.tsk",
        ),
        SoarScoreTaskInfo(
            comp_class="Standard",
            title="Standard Task",
            day_no=1,
            task_no=1,
            timestamp="now",
            task_url="http://soarscore.com/standard.tsk",
        ),
    ]

    # Task title and other data should be displayed
    await act.wait_for_tasks()
    rendered = wtb.render()
    assert "Today's task" in rendered
    assert "Club Task day 1 task 1" in rendered
    assert "Generated on now" in rendered
    assert "Download" in rendered
    assert "Refresh" in rendered


@pytest.mark.asyncio
async def test_taskdownload_task_download(
    storage_dir, soarscore, widget_testbed
) -> None:

    state = {"downloading_task": None}

    def _on_download_task(ev, task):
        state["downloading_task"] = task

    comp = storage.StoredCompetition(
        "test",
        "Test Competition",
        soaringspot_url="http://soaringspot.com/test",
        selected_class="Club",
    )
    act = ActivityStub(urwid.SolidFill("T"))
    wdg = TaskDownloadWidget(act, comp)
    urwid.connect_signal(wdg, "download", _on_download_task)
    wtb = widget_testbed.for_widget(wdg)
    soarscore.tasks = [
        SoarScoreTaskInfo(
            comp_class="Club",
            title="Club Task",
            day_no=1,
            task_no=1,
            timestamp="now",
            task_url="http://soarscore.com/club.tsk",
        ),
        SoarScoreTaskInfo(
            comp_class="Standard",
            title="Standard Task",
            day_no=1,
            task_no=1,
            timestamp="now",
            task_url="http://soarscore.com/standard.tsk",
        ),
    ]

    await act.wait_for_tasks()
    rendered = wtb.render()
    assert "Club Task day 1 task 1" in rendered

    # When we click download
    focused = wtb.get_focus_widgets()[-1]
    assert focused.label == "Download"
    await wtb.keypress("enter")

    # "download" event emits
    assert state["downloading_task"] is not None
    tsk = state["downloading_task"]
    assert tsk.title == "Club Task"


@pytest.mark.asyncio
async def test_taskdownload_refresh_api(storage_dir, soarscore, widget_testbed) -> None:
    comp = storage.StoredCompetition(
        "test",
        "Test Competition",
        soaringspot_url="http://soaringspot.com/test",
        selected_class="Club",
    )
    act = ActivityStub(urwid.SolidFill("T"))
    wdg = TaskDownloadWidget(act, comp)
    wtb = widget_testbed.for_widget(wdg)
    soarscore.tasks = []

    await act.wait_for_tasks()
    rendered = wtb.render()
    assert "No task for today" in rendered

    # When refresh() is called
    soarscore.tasks = [
        SoarScoreTaskInfo(
            comp_class="Club",
            title="Club Task",
            day_no=1,
            task_no=1,
            timestamp="now",
            task_url="http://soarscore.com/club.tsk",
        ),
    ]
    wdg.refresh()

    # Then view should be updated - no todays task in this case
    await act.wait_for_tasks()
    rendered = wtb.render()
    assert "Club Task day 1 task 1" in rendered


@pytest.mark.asyncio
async def test_taskdownload_refresh_btn(storage_dir, soarscore, widget_testbed) -> None:
    comp = storage.StoredCompetition(
        "test",
        "Test Competition",
        soaringspot_url="http://soaringspot.com/test",
        selected_class="Club",
    )
    act = ActivityStub(urwid.SolidFill("T"))
    wdg = TaskDownloadWidget(act, comp)
    wtb = widget_testbed.for_widget(wdg)
    soarscore.tasks = [
        SoarScoreTaskInfo(
            comp_class="Club",
            title="Old Club Task",
            day_no=1,
            task_no=1,
            timestamp="yesteday",
            task_url="http://soarscore.com/club.tsk",
        ),
    ]
    await act.wait_for_tasks()
    rendered = wtb.render()
    assert "Old Club Task day 1 task 1" in rendered
    assert "Refresh" in rendered

    # When refresh button is pressed
    soarscore.tasks = [
        SoarScoreTaskInfo(
            comp_class="Club",
            title="New Club Task",
            day_no=2,
            task_no=2,
            timestamp="now",
            task_url="http://soarscore.com/club.tsk",
        ),
    ]
    await wtb.keypress("right", "enter")

    await act.wait_for_tasks()
    rendered = wtb.render()
    assert "New Club Task day 2 task 2" in rendered


@pytest.mark.asyncio
async def test_taskdownload_fetch_error(storage_dir, soarscore, widget_testbed) -> None:
    comp = storage.StoredCompetition(
        "test",
        "Test Competition",
        soaringspot_url="http://soaringspot.com/test",
        selected_class="Club",
    )
    act = ActivityStub(urwid.SolidFill("T"))
    wdg = TaskDownloadWidget(act, comp)
    wtb = widget_testbed.for_widget(wdg)
    soarscore.tasks = []

    await act.wait_for_tasks()
    rendered = wtb.render()
    assert "No task for today" in rendered
    assert "Refresh" in rendered

    soarscore.fetch_latest_tasks_exc = SoarScoreClientError("Internet error")
    focused = wtb.get_focus_widgets()[-1]
    assert focused.label == " Refresh "
    await wtb.keypress("enter")

    await act.wait_for_tasks()
    assert "Error fetching today's task: Internet error" in wtb.render()


@pytest.mark.asyncio
async def test_taskdownload_no_ss_url(storage_dir, soarscore, widget_testbed) -> None:
    comp = storage.StoredCompetition("test", "Test Competition",)
    act = ActivityStub(urwid.SolidFill("T"))
    wdg = TaskDownloadWidget(act, comp)
    wtb = widget_testbed.for_widget(wdg)
    # When soaringspot url is missing, do not fetch current tasks
    rendered = wtb.render()
    assert rendered.strip() == ""

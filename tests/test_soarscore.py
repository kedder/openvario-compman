import os

import pytest
import mock

from compman import soarscore


HERE = os.path.dirname(__file__)
SOARSCORE_DIR = os.path.join(HERE, "fixtures", "soarscore")


@pytest.mark.asyncio
async def test_soarscore_two_classes(monkeypatch) -> None:
    # GIVEN
    with open(os.path.join(SOARSCORE_DIR, "two-classes.html"), "rb") as f:
        html = f.read()
    get_mock = mock.Mock(name="get")
    resp = mock.Mock()
    resp.content = html
    get_mock.return_value = resp
    monkeypatch.setattr("compman.soarscore.requests.get", get_mock)

    # WHEN
    tasks = await soarscore.fetch_latest_tasks("test")

    # THEN
    assert len(tasks) == 2


def test_parse_soarscore_description() -> None:
    taskinfo = soarscore.parse_soarscore_description("http://task", "")
    assert taskinfo is None

    taskinfo = soarscore.parse_soarscore_description(
        "http://task",
        "Club Day6 Task5 AAT 159/361km .tsk generated: 01-07-2020 21:35:04",
    )
    assert taskinfo is not None
    assert taskinfo.task_url == "http://task"
    assert taskinfo.comp_class == "Club"
    assert taskinfo.day_no == 6
    assert taskinfo.task_no == 5
    assert taskinfo.timestamp == "01-07-2020 21:35:04"

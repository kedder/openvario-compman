import asyncio

import pytest
import urwid

from compman.ui.activity import Activity
from compman.ui.classselector import CompetitionClassSelectorWidget
from compman import storage
from compman.soaringspot import SoaringSpotClientError


class ActivityStub(Activity):
    async def wait_for_tasks(self) -> None:
        await asyncio.wait(self._tasks)


@pytest.mark.asyncio
async def test_classselector_no_comp_url(storage_dir, widget_testbed) -> None:
    # GIVEN
    comp = storage.StoredCompetition("test", "Test Competition")
    act = ActivityStub(urwid.SolidFill("T"))

    # WHEN
    wdg = CompetitionClassSelectorWidget(act, comp)
    wtb = widget_testbed.for_widget(wdg)
    await act.wait_for_tasks()

    # THEN
    rendered = wtb.render()

    # When soaringspot url is not specified, we don't render class selector
    assert rendered.strip() == ""


@pytest.mark.asyncio
async def test_classselector_initial_selection(
    storage_dir, soaringspot, widget_testbed
) -> None:
    # GIVEN
    comp = storage.StoredCompetition(
        "test", "Test Competition", soaringspot_url="http://soaringspot.com/test"
    )
    act = ActivityStub(urwid.SolidFill("T"))

    soaringspot.classes = ["Club", "Standard", "15 Meter"]

    wdg = CompetitionClassSelectorWidget(act, comp)
    wtb = widget_testbed.for_widget(wdg)

    # Initially the progress message is shown
    await asyncio.sleep(0)
    assert "Fetching competition classes" in wtb.render()

    # When classes are fetched, picker is shown
    await act.wait_for_tasks()
    rendered = wtb.render()
    assert "Pick your competition class:" in rendered
    assert "( ) Club" in rendered
    assert "( ) Standard" in rendered
    assert "( ) 15 Meter" in rendered

    # Select "Standard" class. Initially the last class is selected
    await wtb.keypress("up", "enter")
    rendered = wtb.render()
    assert "Competition class" in rendered
    assert "Standard" in rendered
    assert "Club" not in rendered
    assert "Change" in rendered

    # Competition class is selected
    assert comp.classes == ["Club", "Standard", "15 Meter"]
    assert comp.selected_class == "Standard"


@pytest.mark.asyncio
async def test_classselector_change_class(
    storage_dir, soaringspot, widget_testbed
) -> None:
    # GIVEN
    soaringspot.classes = ["Club", "Standard", "15 Meter"]
    comp = storage.StoredCompetition(
        "test",
        "Test Competition",
        soaringspot_url="http://soaringspot.com/test",
        classes=["Club", "Standard"],
        selected_class="Club",
    )

    act = ActivityStub(urwid.SolidFill("T"))
    wdg = CompetitionClassSelectorWidget(act, comp)
    wtb = widget_testbed.for_widget(wdg)

    rendered = wtb.render()
    assert "Competition class" in rendered
    assert "Club" in rendered

    # Press "Change"
    focused = wtb.get_focus_widgets()[-1]
    assert "Change" in focused.label
    await wtb.keypress("enter")

    # We start to fetch classes, but allow to select from known ones
    rendered = wtb.render()
    assert "Fetching competition classes..." in rendered
    assert "(X) Club" in rendered
    assert "( ) Standard" in rendered
    assert "15 Meter" not in rendered

    # When fetching completed, 15 meter class is available for selection
    await act.wait_for_tasks()
    rendered = wtb.render()
    assert "(X) Club" in rendered
    assert "( ) Standard" in rendered
    assert "( ) 15 Meter" in rendered


@pytest.mark.asyncio
async def test_classselector_cancel_selection(
    storage_dir, soaringspot, widget_testbed
) -> None:

    soaringspot.classes = []
    comp = storage.StoredCompetition(
        "test",
        "Test Competition",
        soaringspot_url="http://soaringspot.com/test",
        classes=["Club", "Standard"],
        selected_class="Club",
    )

    act = ActivityStub(urwid.SolidFill("T"))
    wdg = CompetitionClassSelectorWidget(act, comp)
    wtb = widget_testbed.for_widget(wdg)

    rendered = wtb.render()
    assert "Competition class" in rendered
    assert "Club" in rendered

    # Press "Change"
    focused = wtb.get_focus_widgets()[-1]
    assert "Change" in focused.label
    await wtb.keypress("enter")

    # There are no classes for this competition anymore
    await act.wait_for_tasks()
    rendered = wtb.render()

    assert "No classes available for this competition" in rendered
    assert "Club" not in rendered
    assert "Standard" not in rendered
    assert "Cancel" in rendered

    # Press cancel
    await wtb.keypress("down")
    focused = wtb.get_focus_widgets()[-1]
    assert "Cancel" in focused.label
    await wtb.keypress("enter")

    # Previously selected class is kept around
    rendered = wtb.render()
    assert "Competition class" in rendered
    assert "Club" in rendered

    assert wdg.selectable() is False


@pytest.mark.asyncio
async def test_classselector_fetch_error(
    storage_dir, soaringspot, widget_testbed
) -> None:

    comp = storage.StoredCompetition(
        "test", "Test Competition", soaringspot_url="http://soaringspot.com/test"
    )
    act = ActivityStub(urwid.SolidFill("T"))

    soaringspot.fetch_clases_exc = SoaringSpotClientError("Test error")

    wdg = CompetitionClassSelectorWidget(act, comp)
    wtb = widget_testbed.for_widget(wdg)

    await act.wait_for_tasks()
    assert "Error fetching competition classes: Test error" in wtb.render()

from typing import Optional
import asyncio

import urwid
import pytest

from compman import storage
from compman.ui.activity import Activity
from compman.ui.welcome import WelcomeScreen


class ActivityStub(Activity):
    _result: Optional[object] = None

    def __init__(
        self, container, monitor: "ActivityMonitor", result: Optional[object]
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


class ActivityMonitor:
    def __init__(self, result: object = None) -> None:
        self.result = result
        self.created = False
        self.shown = False

    def create(self, container):
        return ActivityStub(container, self, self.result)


class ActivityMocker:
    def __init__(self, mocker) -> None:
        self.mocker = mocker

    def mock(self, spec, result: object = None) -> ActivityMonitor:
        monitor = ActivityMonitor(result)
        self.mocker.patch(spec, monitor.create)
        return monitor


@pytest.fixture
def activity_mocker(mocker):
    yield ActivityMocker(mocker)


def test_welcomescreen_view() -> None:
    # View is opened with the welcome message
    # GIVEN
    container = urwid.WidgetPlaceholder(urwid.SolidFill("X"))
    screen = WelcomeScreen(container)
    screen.show()

    # WHEN
    contents = _render(container)

    # THEN
    assert "Welcome to Competition Manager" in contents
    assert "Set Up a Competition" in contents


@pytest.mark.asyncio
async def test_welcomescreen_setup_comp(
    storage_dir, soaringspot, activity_mocker
) -> None:
    # User picks a competition and end up in competition details screen
    # GIVEN
    sspicker_screen = activity_mocker.mock(
        "compman.ui.soaringspot.SoaringSpotPickerScreen"
    )
    sspicker_screen.result = storage.StoredCompetition(
        id="test", title="Test", soaringspot_url="http://test"
    )
    details_screen = activity_mocker.mock(
        "compman.ui.compdetails.CompetitionDetailsScreen"
    )

    container = urwid.WidgetPlaceholder(urwid.SolidFill("X"))
    screen = WelcomeScreen(container)
    screen.show()

    # WHEN
    handled = container.keypress((0, 0), "enter")
    assert handled is None
    await screen.gather()

    # THEN
    assert sspicker_screen.shown
    assert details_screen.shown
    assert storage.get_settings().current_competition_id == "test"


@pytest.mark.asyncio
async def test_welcomescreen_setup_cancelled(soaringspot, activity_mocker) -> None:
    # User chooses to set up the competition but presses escape and gets back
    # to welcome screen.
    sspicker_screen = activity_mocker.mock(
        "compman.ui.soaringspot.SoaringSpotPickerScreen"
    )
    details_screen = activity_mocker.mock(
        "compman.ui.compdetails.CompetitionDetailsScreen"
    )
    container = urwid.WidgetPlaceholder(urwid.SolidFill("X"))
    screen = WelcomeScreen(container)
    screen.show()

    # WHEN
    container.keypress((0, 0), "enter")
    await asyncio.sleep(0)
    container.keypress((0, 0), "esc")
    await asyncio.sleep(0)
    await screen.gather()

    # THEN
    assert sspicker_screen.shown
    assert not details_screen.shown

    contents = _render(container)
    assert "Welcome to Competition Manager" in contents
    assert "Set Up a Competition" in contents


def _render(widget: urwid.Widget) -> str:
    canvas = widget.render((60, 40))
    contents = [t.decode("utf-8") for t in canvas.text]
    return "\n".join(contents)

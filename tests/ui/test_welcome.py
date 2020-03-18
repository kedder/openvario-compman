import asyncio

import urwid
import pytest

from compman.ui.welcome import WelcomeScreen


def test_welcomescreen_view() -> None:
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
async def test_welcomescreen_setup_comp(soaringspot) -> None:
    # GIVEN
    container = urwid.WidgetPlaceholder(urwid.SolidFill("X"))
    screen = WelcomeScreen(container)
    screen.show()

    # WHEN
    handled = container.keypress((0, 0), "enter")
    assert handled is None
    await asyncio.sleep(0)

    # THEN
    handled = container.keypress((0, 0), "esc")
    assert handled is None


def _render(widget: urwid.Widget) -> str:
    canvas = widget.render((60, 40))
    contents = [t.decode("utf-8") for t in canvas.text]
    return "\n".join(contents)

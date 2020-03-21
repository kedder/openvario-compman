import pytest

from compman import main


@pytest.mark.asyncio
async def test_main(mocker, activity_testbed) -> None:
    # GIVEN
    mocker.patch("compman.main.xcsoar")
    mocker.patch("compman.main.storage")
    mocker.patch("compman.main.logging")
    mocker.patch("compman.main.urwid")
    mocker.patch("compman.ui.mainmenu.MainMenuScreen")

    main.run([])


def test_debounce_esc() -> None:
    assert main.debounce_esc(["down"], []) == ["down"]
    assert main.debounce_esc(["down", "down"], []) == ["down", "down"]
    assert main.debounce_esc(["esc"], []) == ["esc"]
    assert main.debounce_esc(["esc", "esc"], []) == ["esc"]
    assert main.debounce_esc(["esc", "esc", "esc"], []) == ["esc", "esc"]
    assert main.debounce_esc(["esc", "down", "esc"], []) == ["esc", "down", "esc"]

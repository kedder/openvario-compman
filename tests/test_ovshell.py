import asyncio

import pytest

from ovshell.testing import OpenVarioShellStub
from compman.ovshell import extension, CompmanShellApp, CompmanShellActivity


@pytest.fixture
def ovshell(tmp_path: str) -> OpenVarioShellStub:
    return OpenVarioShellStub(tmp_path)


@pytest.fixture
def compman_app(
    ovshell: OpenVarioShellStub, tmp_path: str, monkeypatch, xcsoar_dir: str
) -> CompmanShellApp:
    app = CompmanShellApp(ovshell)
    monkeypatch.setenv("COMPMAN_XCSOARDIR", str(xcsoar_dir))
    monkeypatch.setenv("COMPMAN_DATADIR", str(tmp_path))
    return app


def test_extension(ovshell: OpenVarioShellStub) -> None:
    # WHEN
    ext = extension("compman", ovshell)

    apps = ext.list_apps()
    assert len(apps) == 1


def test_launch_app(ovshell: OpenVarioShellStub, compman_app: CompmanShellApp) -> None:
    # WHEN
    compman_app.launch()

    # THEN
    act = ovshell.screen.stub_top_activity()
    assert isinstance(act, CompmanShellActivity)


def test_ovshell_activity(
    ovshell: OpenVarioShellStub, compman_app: CompmanShellApp
) -> None:
    # WHEN
    compman_app.launch()
    act = ovshell.screen.stub_top_activity()
    assert act is not None
    widget = act.create()

    # THEN
    canvas = widget.render((60, 30))
    contents = "\n".join([t.decode("utf-8") for t in canvas.text])
    assert "Welcome to Competition Manager" in contents


@pytest.mark.asyncio
async def test_ovshell_exit_app(
    ovshell: OpenVarioShellStub, compman_app: CompmanShellApp
) -> None:
    # WHEN
    compman_app.launch()
    act = ovshell.screen.stub_top_activity()
    assert act is not None
    widget = act.create()

    widget.keypress((60, 30), "esc")
    await asyncio.sleep(0)

    canvas = widget.render((60, 30))
    contents = "\n".join([t.decode("utf-8") for t in canvas.text])
    assert "Main Menu" in contents

    widget.keypress((60, 30), "esc")
    await asyncio.sleep(0)

    # THEN
    assert ovshell.screen.stub_top_activity() is None

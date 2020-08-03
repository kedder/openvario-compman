from typing import Sequence
import os

import urwid
from ovshell import api

from compman import storage
from compman import xcsoar
from compman import main
from compman.ui.mainmenu import MainMenuScreen


def extension(id: str, shell: api.OpenVarioShell) -> api.Extension:
    return CompmanExtension(id, shell)


class CompmanExtension(api.Extension):
    title = "Compman"

    def __init__(self, id: str, shell: api.OpenVarioShell) -> None:
        self.id = id
        self.shell = shell

    def list_apps(self) -> Sequence[api.App]:
        return [CompmanShellApp(self.shell)]


class CompmanShellApp(api.App):
    name = "compman"
    title = "Compman"
    description = "Competition manager"
    priority = 70

    def __init__(self, shell: api.OpenVarioShell) -> None:
        self.shell = shell

    def launch(self) -> None:
        datadir = os.environ.get("COMPMAN_DATADIR", storage.DEFAULT_DATADIR)
        datadir = os.path.expanduser(datadir)
        storage.init(datadir)
        xcsoardir = os.environ.get("COMPMAN_XCSOARDIR", None)
        xcsoar.init(xcsoardir)
        main.setup_logging(datadir)

        act = CompmanShellActivity(self.shell)
        self.shell.screen.push_activity(act, palette=main.PALETTE)


class CompmanShellActivity(api.Activity):
    def __init__(self, shell: api.OpenVarioShell) -> None:
        self.shell = shell

    def create(self) -> urwid.Widget:
        container = urwid.WidgetPlaceholder(urwid.SolidFill(" "))
        screen = MainMenuScreen(container)
        screen.on_exit(self._exit)
        screen.show()
        return container

    def _exit(self) -> None:
        self.shell.screen.pop_activity()

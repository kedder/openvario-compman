import os
import sys
import asyncio
import logging
import argparse

import urwid

from compman import storage
from compman import xcsoar

log = logging.getLogger("compman")


parser = argparse.ArgumentParser(description="Competition manager for Openvario")
parser.add_argument(
    "--datadir",
    default=os.environ.get("COMPMAN_DATADIR", storage.DEFAULT_DATADIR),
    help=(
        "Path to directory where compman stores data. By default "
        "~/.compman. Also can be set with COMPMAN_DATADIR environment variable"
    ),
)
parser.add_argument(
    "--xcsoardir",
    default=os.environ.get("COMPMAN_XCSOARDIR", None),
    help=(
        "Path to xcsoar home directory. By default ~/.xcsoar. Also can be set "
        "with COMPMAN_XCSOARDIR environment variable"
    ),
)


PALETTE = [
    ("text", "white", "black", ""),
    ("btn focus", "white", "dark red", ""),
    ("btn normal", "white", "dark blue", ""),
    ("li normal", "light cyan", "black", ""),
    ("li focus", "white", "dark red", ""),
    ("pg normal", "white", "black", "standout"),
    ("pg complete", "white", "dark magenta"),
    ("pg smooth", "dark magenta", "black"),
    ("screen header", "yellow", "black", ""),
    ("bg", "light gray", "black", ""),
    ("success message", "light green", "black", ""),
    ("success banner", "white", "dark green", ""),
    ("error message", "light red", "black", ""),
    ("error banner", "white", "dark red", ""),
    ("progress", "light magenta", "black", ""),
    ("remark", "dark gray", "black", ""),
]


def exit() -> None:
    raise urwid.ExitMainLoop()


def startui(urwidloop) -> None:
    # Show the splash screen as soon as possible
    urwidloop.draw_screen()

    # We can now import and show the main menu screen
    container = urwid.WidgetPlaceholder(urwid.SolidFill(" "))
    urwidloop.widget = urwid.AttrMap(container, "bg")

    from compman.ui.mainmenu import MainMenuScreen

    screen = MainMenuScreen(container)
    screen.on_exit(exit)
    screen.show()


def debounce_esc(keys, raw):
    # For some weird reason, SteFly remote stick sends two "Escape" key presses
    # when user presses X button once. Whatever reason might be, this is a
    # permanent deision and we have to deal with that. We still want to handle
    # single escape keypresses though, to support input devices that behave
    # sanely.
    filtered = []
    escpressed = False
    for k in keys:
        if k == "esc":
            if escpressed:
                escpressed = False
                filtered.append(k)
            else:
                escpressed = True
        else:
            if escpressed:
                filtered.append("esc")
                escpressed = False
            filtered.append(k)
    if escpressed:
        filtered.append("esc")
    return filtered


def setup_logging(datadir: str) -> None:
    logfname = os.path.join(datadir, "compman.log")
    logging.basicConfig(filename=logfname, level=logging.INFO)
    log.info(f"Starting compman with data dir in '{datadir}'")


def run(argv) -> None:
    args = parser.parse_args(argv)
    datadir = os.path.expanduser(args.datadir)

    storage.init(datadir)
    xcsoar.init(args.xcsoardir)
    setup_logging(datadir)

    asyncioloop = asyncio.get_event_loop()
    asyncioloop.set_debug(True)
    evl = urwid.AsyncioEventLoop(loop=asyncioloop)

    btxt = urwid.BigText("Compman", urwid.font.Thin6x6Font())
    splash = urwid.Filler(urwid.Padding(btxt, "center", "clip"), "middle")
    urwidloop = urwid.MainLoop(
        splash, palette=PALETTE, event_loop=evl, input_filter=debounce_esc
    )

    asyncioloop.call_soon(startui, urwidloop)
    try:
        urwidloop.run()
        log.info("Exiting normally")
    except KeyboardInterrupt:
        log.info("Killed")


def main():
    run(sys.argv[1:])

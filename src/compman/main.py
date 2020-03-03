import os
import asyncio
import logging
import argparse

import urwid

from compman import storage

log = logging.getLogger("compman")


parser = argparse.ArgumentParser(description="test")
parser.add_argument(
    "--datadir",
    default=os.environ.get("COMPMAN_DATADIR", "~/.compman"),
    help=(
        "Path to directory where compman stores data. By default "
        "~/.compman. Also can be set with COMPMAN_DATADIR environment variable"
    ),
)


async def startui(urwidloop):
    container = urwid.WidgetPlaceholder(urwid.SolidFill(" "))
    urwidloop.widget = urwid.AttrMap(container, "bg")

    from compman.ui.mainmenu import MainMenuScreen

    screen = MainMenuScreen(container)
    screen.show()
    await screen.response

    raise urwid.ExitMainLoop()


def main() -> None:
    args = parser.parse_args()
    datadir = os.path.expanduser(args.datadir)

    storage.init(datadir)
    logfname = os.path.join(datadir, "compman.log")
    logging.basicConfig(filename=logfname, level=logging.INFO)
    log.info(f"Starting compman with data dir in '{datadir}'")

    btxt = urwid.BigText("Openvario", urwid.font.Thin6x6Font())
    pad = urwid.Padding(btxt, "center", "clip")
    intro = urwid.Filler(pad, "middle")

    palette = [
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

    asyncioloop = asyncio.get_event_loop()
    asyncioloop.set_debug(True)
    evl = urwid.AsyncioEventLoop(loop=asyncioloop)
    urwidloop = urwid.MainLoop(intro, palette=palette, event_loop=evl)

    amain = startui(urwidloop)
    asyncioloop.create_task(amain)
    try:
        urwidloop.run()
        log.info("Exiting normally")
    except KeyboardInterrupt:
        log.info("Killed")
        pass

import urwid
import asyncio
import logging

from compman import config
from compman import storage
from compman.ui import widget
from compman.ui.soaringspot import SoaringSpotPicker


async def show_progress():
    global progressbar
    for p in range(1000):
        progressbar.set_completion(p / 10 + 1)
        await asyncio.sleep(0.01)


curtask = None
sspicker = None

competitions = []


def make_comp_switcher() -> None:
    def handle_press(ev):
        global curtask
        if curtask != None and not curtask.done():
            curtask.cancel()
        curtask = asyncio.create_task(show_progress())

    # li = widget.CMSelectableListItem("Lietuvos sklandymo čempionatas")
    # urwid.connect_signal(li, "click", handle_press, {"one": "two"})
    # items = [li] * 4

    # hellobtn = widget.CMSelectableListItem("Hello")
    # items.insert(0, hellobtn)

    items = []
    for comp in storage.get_all():
        li = widget.CMSelectableListItem(comp.title)
        urwid.connect_signal(li, "click", handle_press)
        items.append(li)

    lw = urwid.SimpleListWalker(items)
    listbox = urwid.ListBox(lw)
    return listbox


def make_button_row() -> None:
    b1 = widget.CMButton("Refresh")
    b2 = widget.CMButton("Download")
    b3 = widget.CMButton("Help")

    return urwid.Filler(urwid.GridFlow([b1, b2, b3], 15, 2, 1, "center"), "middle")


async def startui(urwidloop):
    container = urwid.WidgetPlaceholder(urwid.SolidFill(' '))
    urwidloop.widget = container

    def_comp_id = config.get().current_competition_id
    comp = None
    if def_comp_id:
        comp = storage.load_competiton(def_comp_id)

    if comp is None:
        from compman.ui.welcome import WelcomeScreen
        screen = WelcomeScreen(container)
        # urwidloop.widget = screen.view
        comp = await screen.response

    from compman.ui.compdetails import CompetitionDetailsScreen
    screen = CompetitionDetailsScreen(container, comp)

    await screen.response

    # global sspicker

    # contents1 = make_comp_switcher()
    # sspicker = SoaringSpotPicker()

    # upperbox = urwid.LineBox(contents1, "My Competitions", title_align="left")
    # lowerbox = urwid.LineBox(sspicker, "Add a Competition", title_align="left")

    # buttonrow = make_button_row()

    # mainview = urwid.Pile([(10, upperbox), lowerbox, (3, buttonrow)])

    # # footer = urwid.LineBox(urwid.Text(u"Competition Manager"))
    # global progressbar
    # progressbar = footer = urwid.ProgressBar("pg normal", "pg complete", current=82.5)
        # frame = urwid.Frame(mainview, footer=footer)
    # main = urwid.AttrMap(frame, "bg")
    # urwidloop.widget = main

def exception_handler(loop, context):
    logging.error(f"ASYNCIO ERROR, {context}")


def main() -> None:
    # btxt.set_text('hello')
    # Read config
    logging.basicConfig(filename='compman.log',level=logging.DEBUG)

    cfg = config.load()
    config.set(cfg)

    storage.init()

    # mainwidget = urwid.SolidFill('X')
    btxt = urwid.BigText(u"Openvario", urwid.font.Thin6x6Font())
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
        ("bg", "dark gray", "black"),
    ]

    asyncioloop = asyncio.get_event_loop()
    asyncioloop.set_debug(True)
    evl = urwid.AsyncioEventLoop(loop=asyncioloop)
    urwidloop = urwid.MainLoop(intro, palette=palette, event_loop=evl)
    global amain
    amain = startui(urwidloop)
    asyncioloop.set_exception_handler(exception_handler)
    asyncioloop.create_task(amain)
    try:
        urwidloop.run()
    except KeyboardInterrupt:
        pass

import urwid
import asyncio

from compman.ui import widget
from compman.ui.soaringspot import SoaringSpotPicker, SoaringSpotCompetition


async def show_progress():
    global progressbar
    for p in range(1000):
        progressbar.set_completion(p / 10 + 1)
        await asyncio.sleep(0.01)


curtask = None
sspicker = None

competitions = []


def make_comp_switcher() -> None:
    def handle_press(ev, data):
        global competitions
        comp = SoaringSpotCompetition(
            "New Comp. The name they picked is really really long. How did they care to type that much?",
            "Description that is really really long. Doesn't fit in one line at all.",
        )
        competitions.append(comp)
        sspicker.set_competitions(competitions)

        global curtask
        if curtask != None and not curtask.done():
            curtask.cancel()
        curtask = asyncio.create_task(show_progress())

    li = widget.CMSelectableListItem("Lietuvos sklandymo čempionatas")
    urwid.connect_signal(li, "click", handle_press, {"one": "two"})
    items = [li] * 4

    hellobtn = widget.CMSelectableListItem("Hello")
    items.insert(0, hellobtn)

    lw = urwid.SimpleListWalker(items)
    listbox = urwid.ListBox(lw)
    return listbox


def make_button_row() -> None:
    b1 = widget.CMButton("Refresh")
    b2 = widget.CMButton("Download")
    b3 = widget.CMButton("Help")

    return urwid.Filler(urwid.GridFlow([b1, b2, b3], 15, 2, 1, "center"), "middle")


async def startui(urwidloop):
    await asyncio.sleep(1)

    global sspicker

    contents1 = make_comp_switcher()
    sspicker = SoaringSpotPicker()

    upperbox = urwid.LineBox(contents1, "My Competitions", title_align="left")
    lowerbox = urwid.LineBox(sspicker, "Add a Competition", title_align="left")

    buttonrow = make_button_row()

    mainview = urwid.Pile([(10, upperbox), lowerbox, (3, buttonrow)])

    # footer = urwid.LineBox(urwid.Text(u"Competition Manager"))
    global progressbar
    progressbar = footer = urwid.ProgressBar("pg normal", "pg complete", current=82.5)
    frame = urwid.Frame(mainview, footer=footer)
    main = urwid.AttrMap(frame, "bg")
    urwidloop.widget = main


def main() -> None:
    # btxt.set_text('hello')

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
    evl = urwid.AsyncioEventLoop(loop=asyncioloop)
    urwidloop = urwid.MainLoop(intro, palette=palette, event_loop=evl)
    asyncioloop.create_task(startui(urwidloop))
    try:
        urwidloop.run()
    except KeyboardInterrupt:
        pass

import urwid
import asyncio
import logging

from compman import config
from compman import storage


async def startui(urwidloop):
    container = urwid.WidgetPlaceholder(urwid.SolidFill(" "))
    urwidloop.widget = urwid.AttrMap(container, 'bg')

    # from compman.ui.welcome import WelcomeScreen
    # screen = WelcomeScreen(container)
    # screen.show()
    # # urwidloop.widget = screen.view
    # comp = await screen.response

    # from compman.ui.selectcomp import SelectCompetitionScreen
    # screen = SelectCompetitionScreen(container)
    # await screen.response


    # def_comp_id = config.get().current_competition_id
    # comp = None
    # if def_comp_id:
    #     comp = storage.load_competiton(def_comp_id)

    # if comp is None:
    #     from compman.ui.welcome import WelcomeScreen

    #     screen = WelcomeScreen(container)
    #     # urwidloop.widget = screen.view
    #     comp = await screen.response

    # from compman.ui.compdetails import CompetitionDetailsScreen
    # screen = CompetitionDetailsScreen(container)
    # await screen.response

    from compman.ui.mainmenu import MainMenuScreen
    screen = MainMenuScreen(container)
    screen.show()
    await screen.response

    raise urwid.ExitMainLoop()


def main() -> None:
    # btxt.set_text('hello')
    # Read config
    logging.basicConfig(filename="compman.log", level=logging.DEBUG)

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
    global amain
    amain = startui(urwidloop)
    asyncioloop.create_task(amain)
    try:
        urwidloop.run()
    except KeyboardInterrupt:
        pass

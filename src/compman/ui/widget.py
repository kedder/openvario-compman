from typing import Optional, List, Union, Tuple
import asyncio
import logging

import urwid


log = logging.getLogger("compman")

UrwidMarkup = Union[str, Tuple[str, str], List[Union[str, Tuple[str, str]]]]


class CMButton(urwid.Button):
    def __init__(self, text):
        super().__init__(text)
        self.txt = urwid.SelectableIcon(text)
        self.txt.align = "center"
        btn = urwid.AttrWrap(self.txt, "btn normal", "btn focus")
        self._w = btn

    def set_text(self, text: str):
        self.txt.set_text(text)


class CMSelectableListItem(urwid.Button):
    def __init__(self, text):
        super().__init__(text)
        btn = urwid.SelectableIcon(text)
        wdg = urwid.AttrMap(btn, "li normal", "li focus")
        self._w = wdg

    def _btnclicked(self, btn):
        self._emit("selected")


class CMScreenPadding(urwid.Padding):
    def __init__(self, w):
        super().__init__(w, width=(urwid.RELATIVE, 92), align=urwid.CENTER)


class CMScreenHeader(urwid.WidgetWrap):
    def __init__(self, text: str) -> None:
        orig = urwid.AttrMap(
            urwid.Pile(
                [
                    urwid.Divider(),
                    CMScreenPadding(urwid.Text(text)),
                    urwid.Divider("─"),
                    urwid.Divider(),
                ]
            ),
            "screen header",
        )
        super().__init__(orig)


class CMFlashMessage(urwid.WidgetWrap):
    _flashtask: Optional[asyncio.Task]

    def __init__(self, activity) -> None:
        self.text = urwid.Text("")
        self._activity = activity
        self._flashtask = None
        super().__init__(self.text)

    def set(self, markup: UrwidMarkup):
        self.text.set_text(markup)

    def flash(self, markup: UrwidMarkup) -> None:
        if self._flashtask and not self._flashtask.done():
            self._flashtask.cancel()
        self._flashtask = self._activity.async_task(self._flash_status(markup))

    async def _flash_status(self, markup: UrwidMarkup):
        self.text.set_text(markup)
        await asyncio.sleep(3.0)
        self.text.set_text("")


class CMGlobalCommands(urwid.WidgetWrap):
    def __init__(self, widget, activity):
        super().__init__(widget)
        self.activity = activity

    def keypress(self, size, key):
        if key == "esc":
            self.activity.finish(None)
            return
        return self._w.keypress(size, key)

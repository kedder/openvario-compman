import asyncio
import urwid


class CMButton(urwid.Button):
    def __init__(self, text):
        super().__init__(text)
        txt = urwid.SelectableIcon(text)
        txt.align = "center"
        btn = urwid.AttrWrap(txt, "btn normal", "btn focus")
        self._w = btn


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
    def __init__(self) -> None:
        self.text = urwid.Text("")
        self._flashtask = None
        super().__init__(self.text)

    def flash(self, markup: str):
        if self._flashtask and not self._flashtask.done():
            self._flashtask.cancel()
        self._flashtask = asyncio.create_task(self._flash_status(markup))

    async def _flash_status(self, markup: str):
        self.text.set_text(markup)
        await asyncio.sleep(3.0)
        self.text.set_text("")

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

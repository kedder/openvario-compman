import asyncio
from typing import List, Tuple

import urwid


class WidgetTestbed:
    def __init__(self, wdg: urwid.Widget) -> None:
        self.wdg = wdg

    def render(self, size=(60, 30)) -> str:
        if "flow" in self.wdg.sizing():
            size = size[:1]
        canvas = self.wdg.render(size)
        contents = [t.decode("utf-8") for t in canvas.text]
        return "\n".join(contents)

    def get_focus_widgets(self) -> List[urwid.Widget]:
        container = self._find_container_widget(self.wdg)
        return container.get_focus_widgets()

    async def keypress(self, *keys: str) -> None:
        size: Tuple[int, ...] = (60, 30)
        if "flow" in self.wdg.sizing():
            size = size[:1]

        for key in keys:
            res = self.wdg.keypress(size, key)
            assert res is None, "Keypress is not processed"
            await asyncio.sleep(0)

    def _find_container_widget(self, w: urwid.Widget) -> urwid.WidgetContainerMixin:
        if isinstance(w, urwid.WidgetContainerMixin):
            return w
        if isinstance(w, urwid.WidgetDecoration):
            return self._find_container_widget(w.original_widget)
        if isinstance(w, urwid.WidgetWrap):
            return self._find_container_widget(w._w)
        raise RuntimeError(f"Unknown widget type: {w}")


class WidgetTestbedFactory:
    def for_widget(self, wdg: urwid.Widget) -> WidgetTestbed:
        return WidgetTestbed(wdg)

import logging
from typing import List

import urwid

from compman import soaringspot, storage
from compman.ui import widget
from compman.ui.activity import Activity

log = logging.getLogger("compman")


class CompetitionClassSelectorWidget(urwid.WidgetWrap):
    signals = ["change"]

    def __init__(self, activity: Activity, comp: storage.StoredCompetition) -> None:
        self._activity = activity
        self._comp = comp

        if self._comp.selected_class is None:
            curview = self._create_class_selector()
        else:
            curview = self._create_class_display()
        self.container = urwid.WidgetPlaceholder(curview)
        super().__init__(self.container)

    def selectable(self):
        return bool(self._comp.classes)

    def _create_class_selector(self) -> urwid.Widget:
        self._activity.async_task(self._update_classes())

        self.class_group: List[urwid.Widget] = []
        self.class_pile = urwid.Pile([])
        self._populate_class_radios()
        self.status = urwid.Text("")

        if self._comp.selected_class:
            cancel_btn = widget.CMButton(" Cancel ")
            urwid.connect_signal(cancel_btn, "click", self._on_cancel_change_class)
        else:
            cancel_btn = urwid.Text("")

        return urwid.Pile(
            [
                self.status,
                self.class_pile,
                urwid.Divider(),
                widget.ButtonRow([cancel_btn]),
            ]
        )

    def _create_class_display(self) -> urwid.Widget:
        button = widget.CMButton(" Change ")
        urwid.connect_signal(button, "click", self._on_change_class)

        class_title = urwid.Text(("highlight", self._comp.selected_class))

        return urwid.Pile(
            [
                urwid.Columns(
                    [("pack", urwid.Text("Competition class")), ("pack", button)],
                    dividechars=1,
                ),
                urwid.Padding(class_title, left=2),
            ]
        )

    async def _update_classes(self) -> None:
        if self._comp.soaringspot_url is None:
            return
        self.status.set_text(("progress", "Fetching competition classes..."))
        try:
            classes = await soaringspot.fetch_classes(self._comp.soaringspot_url)
        except soaringspot.SoaringSpotClientError as e:
            self.status.set_text(
                ("error message", f"Error fetching competition classes: {e}")
            )
            log.exception("Error fetching competition classes")
            return

        self._comp.classes = classes
        storage.save_competition(self._comp)
        self._populate_class_radios()
        if classes:
            self.status.set_text("Pick your competition class:")
        else:
            self.status.set_text(
                ("remark", "No classes available for this competition")
            )

    def _populate_class_radios(self) -> None:
        radios = []
        for cls in self._comp.classes:
            radio = urwid.RadioButton(
                self.class_group, cls, cls == self._comp.selected_class
            )
            urwid.connect_signal(radio, "change", self._on_class_selected, cls)
            radio = urwid.AttrMap(radio, "li normal", "li focus")
            radios.append(urwid.Padding(radio, left=2))

        self.class_pile.contents = [(r, ("pack", None)) for r in radios]
        self.class_pile._selectable = True

    def _on_cancel_change_class(self, ev):
        wdg = self._create_class_display()
        self.container.original_widget = wdg

    def _on_change_class(self, ev):
        wdg = self._create_class_selector()
        self.container.original_widget = wdg

    def _on_class_selected(self, ev, new_state, new_class):
        if new_state:
            self._comp.selected_class = new_class
            storage.save_competition(self._comp)
            self._emit("change", new_class)

            wdg = self._create_class_display()
            self.container.original_widget = wdg

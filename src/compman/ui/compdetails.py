from typing import List, Optional, cast
import logging
import asyncio

import urwid

from compman import storage
from compman import soaringspot
from compman import soarscore
from compman import http
from compman import xcsoar
from compman.ui import widget
from compman.ui.activity import Activity

nothing = urwid.Pile([])

log = logging.getLogger("compman")


class CompetitionDetailsScreen(Activity):
    def show(self):
        cid = storage.get_settings().current_competition_id
        self.competition = storage.load_competition(cid)
        self.airspaces = storage.get_airspace_files(cid)
        self.waypoints = storage.get_waypoint_files(cid)
        self.profiles = xcsoar.list_xcsoar_profiles()

        super().show()
        self._flashtask = None
        self.async_task(self._update_competition_files())

    def create_view(self) -> urwid.Widget:
        p2 = lambda w: urwid.Padding(w, left=2)

        self.class_widget = CompetitionClassSelectorWidget(self, self.competition)
        urwid.connect_signal(self.class_widget, "change", self._on_class_changed)

        self.task_widget = TaskDownloadWidget(self, self.competition)
        urwid.connect_signal(self.task_widget, "download", self._on_download_task)

        self.airspace_group: List[urwid.Widget] = []
        self.airspace_pile = urwid.Pile(
            [
                self._make_file_radio(
                    sf,
                    self.airspace_group,
                    sf.name == self.competition.airspace,
                    self._on_airspace_changed,
                )
                for sf in self.airspaces
            ]
        )

        self.waypoint_group: List[urwid.Widget] = []
        self.waypoint_pile = urwid.Pile(
            [
                self._make_file_radio(
                    sf,
                    self.waypoint_group,
                    sf.name == self.competition.waypoints,
                    self._on_waypoint_changed,
                )
                for sf in self.waypoints
            ]
        )

        self.profile_pile = urwid.Pile(
            [self._make_profile_checkbox(prf) for prf in self.profiles]
        )

        self.download_status = urwid.Text("")

        form = urwid.Pile(
            [
                self.class_widget,
                urwid.Divider(),
                self.task_widget,
                urwid.Divider(),
                self.download_status,
                urwid.Divider(),
                urwid.Text("Airspace files"),
                p2(self.airspace_pile),
                urwid.Divider(),
                urwid.Text("Waypoint files"),
                p2(self.waypoint_pile),
                urwid.Divider(),
                urwid.Text("XCSoar profiles"),
                p2(self.profile_pile),
                urwid.Divider(),
                self._create_buttons(),
            ]
        )

        filler = urwid.Filler(form, valign=urwid.TOP)

        self.status = widget.CMFlashMessage(self)

        return urwid.Frame(
            widget.CMScreenPadding(filler),
            header=widget.CMScreenHeader(self.competition.title),
            footer=widget.CMScreenPadding(self.status),
        )

    def _create_buttons(self):
        activate_btn = widget.CMButton("Activate")
        urwid.connect_signal(activate_btn, "click", self._on_activate)

        exit_btn = widget.CMButton("Main Menu")
        urwid.connect_signal(exit_btn, "click", self._on_exit)
        return button_row([activate_btn, exit_btn])

    def _on_airspace_changed(self, ev, new_state, selected):
        if not new_state:
            return
        self.competition.airspace = selected
        storage.save_competition(self.competition)
        self._udpate_xcsoar_config(self.competition)
        self.status.flash(f"Airspace changed to: {selected}")

    def _on_waypoint_changed(self, ev, new_state, selected):
        if not new_state:
            return
        self.competition.waypoints = selected
        storage.save_competition(self.competition)
        self._udpate_xcsoar_config(self.competition)
        self.status.flash(f"Waypoint changed to: {selected}")

    def _on_profile_changed(self, ev, selected, profile: str) -> None:
        if selected:
            self.competition.add_profile(profile)
        else:
            self.competition.remove_profile(profile)
        storage.save_competition(self.competition)

    def _on_download_task(self, ev, task):
        self.async_task(self._download_task(task))

    def _on_class_changed(self, ev, new_class):
        self.task_widget.refresh()

    async def _download_task(self, taskinfo: soarscore.SoarScoreTaskInfo) -> None:
        self.status.set(("progress", f"Downloading {taskinfo.title}..."))
        task = await soarscore.fetch_url(taskinfo.task_url)
        taskfname = xcsoar.install_default_task(task)
        self.status.flash(
            ("success message", f"Task downloaded and installed: {taskfname}")
        )

    def _on_activate(self, btn) -> None:
        if not self.competition.profiles:
            self.status.flash(
                ("error message", "Please select at least one XCSoar profile")
            )
            return

        profiles = ", ".join(self.competition.profiles)
        self._udpate_xcsoar_config(self.competition)
        self.status.flash(("success message", f"XCSoar profiles updated: {profiles}"))

    def _on_exit(self, btn):
        self.finish(None)

    def _udpate_xcsoar_config(self, comp: storage.StoredCompetition) -> None:
        for prf in self.competition.profiles:
            xcprofile = xcsoar.get_xcsoar_profile(prf)
            if comp.airspace:
                xcprofile.set_airspace(
                    storage.get_full_file_path(comp.id, comp.airspace)
                )
            if comp.waypoints:
                xcprofile.set_waypoint(
                    storage.get_full_file_path(comp.id, comp.waypoints)
                )
            xcprofile.save()

    async def _update_competition_files(self) -> None:
        compurl = self.competition.soaringspot_url
        if compurl is None:
            return

        self.download_status.set_text(("progress", "Refreshing file list..."))
        downloads = await soaringspot.fetch_downloads(compurl)
        new_airspaces, new_waypoints = self._detect_new_files(downloads)

        if not new_airspaces and not new_waypoints:
            self.download_status.set_text(("remark", "No updates to competition files"))
            return

        self.download_status.set_text(
            ("success message", "New contest files detected!")
        )

        tasks = []
        tasks.extend(
            self._download_new_files(
                new_airspaces,
                self.airspace_pile,
                self.airspace_group,
                self._on_airspace_changed,
            )
        )
        tasks.extend(
            self._download_new_files(
                new_waypoints,
                self.waypoint_pile,
                self.waypoint_group,
                self._on_waypoint_changed,
            )
        )
        await asyncio.gather(*tasks)

    def _detect_new_files(self, downloads):
        DFT = soaringspot.DownloadableFileType
        airspace_files = {f.name for f in self.airspaces}
        dl_airspaces = {d.filename for d in downloads if d.kind == DFT.AIRSPACE}
        new_airspaces = dl_airspaces - airspace_files

        waypoint_files = {f.name for f in self.waypoints}
        dl_waypoints = {d.filename for d in downloads if d.kind == DFT.WAYPOINT}
        new_waypoints = dl_waypoints - waypoint_files

        dl_idx = {d.filename: d for d in downloads}
        return ([dl_idx[f] for f in new_airspaces], [dl_idx[f] for f in new_waypoints])

    def _download_new_files(self, new_files, checkbox_pile, group, select_handler):
        tasks = []
        for sspotfile in new_files:
            sf = storage.StoredFile(name=sspotfile.filename, size=None)
            radio = self._make_file_radio(sf, group, False, select_handler)
            checkbox_pile.contents.insert(0, (radio, ("pack", None)))
            tasks.append(self._download_file(sf, sspotfile.href, radio))

        return tasks

    async def _download_file(
        self, sf: storage.StoredFile, url: str, radio: urwid.RadioButton
    ) -> None:
        orig_radio = radio.original_widget
        orig_radio.set_label(self._make_label(sf, [("progress", "Downloading...")]))
        dlcontents = await http.fetch_file(url)
        stored = storage.store_file(self.competition.id, sf.name, dlcontents)
        orig_radio.set_label(self._make_label(stored, [("success banner", " New! ")]))

    def _make_file_radio(
        self, sf: storage.StoredFile, group, selected: bool, select_handler
    ) -> urwid.RadioButton:
        label = f"{sf.name} ({sf.format_size()})"
        radio = urwid.RadioButton(group, label, selected)
        urwid.connect_signal(radio, "change", select_handler, sf.name)
        return urwid.AttrMap(radio, "li normal", "li focus")

    def _make_label(
        self, sf: storage.StoredFile, extra: widget.UrwidMarkup = None
    ) -> widget.UrwidMarkup:
        label = f"{sf.name} ({sf.format_size()})"
        markup: List[widget.UrwidMarkup] = [label, " "]
        markup.extend(extra or [])
        return cast(widget.UrwidMarkup, markup)

    def _make_profile_checkbox(self, profile: str) -> urwid.CheckBox:
        cb = urwid.CheckBox(profile, profile in self.competition.profiles)
        urwid.connect_signal(cb, "change", self._on_profile_changed, profile)
        return urwid.AttrMap(cb, "li normal", "li focus")


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
            [self.status, self.class_pile, urwid.Divider(), button_row([cancel_btn]),]
        )

    def _create_class_display(self) -> urwid.Widget:
        button = widget.CMButton(" Change Class ")
        urwid.connect_signal(button, "click", self._on_change_class)

        class_title = urwid.Text(("highlight", self._comp.selected_class))

        return urwid.Pile(
            [
                urwid.Text("Competition class"),
                urwid.Padding(class_title, left=2),
                urwid.Divider(),
                button_row([button]),
            ]
        )

    async def _update_classes(self) -> None:
        if self._comp.soaringspot_url is None:
            return
        self.status.set_text(("progress", "Fetching competition classes..."))
        classes = await soaringspot.fetch_classes(self._comp.soaringspot_url)
        self._comp.classes = classes
        storage.save_competition(self._comp)
        if classes:
            self._populate_class_radios()
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


class TaskDownloadWidget(urwid.WidgetWrap):
    signals = ["download"]

    def __init__(self, activity: Activity, comp: storage.StoredCompetition) -> None:
        self._activity = activity
        self._comp = comp
        self._tasks: List[soarscore.SoarScoreTaskInfo] = []

        self._activity.async_task(self._fetch_tasks())
        super().__init__(urwid.Pile([]))

    def refresh(self) -> None:
        self._activity.async_task(self._fetch_tasks())

    async def _fetch_tasks(self) -> None:
        if self._comp.soaringspot_url is None:
            return

        self._w = urwid.Text(("progress", "Fetching today's task..."))

        self._tasks = await soarscore.fetch_latest_tasks(self._comp.id)
        self._create_task_view()

    def _get_task(self) -> Optional[soarscore.SoarScoreTaskInfo]:
        for ti in self._tasks:
            if ti.comp_class == self._comp.selected_class:
                return ti
        return None

    def _create_task_view(self) -> None:
        if self._comp.selected_class is None:
            self._w = urwid.Text(
                ("remark", "Select competition class to download task")
            )
            return

        refresh_btn = widget.CMButton(" Refresh ")
        urwid.connect_signal(refresh_btn, "click", self._on_refresh)

        curtask = self._get_task()
        if curtask is None:
            self._w = urwid.Columns(
                [
                    ("pack", urwid.Text(("remark", "No task for today"))),
                    ("pack", refresh_btn),
                ],
                dividechars=1,
            )
            return

        task_title = urwid.Text(
            [
                ("highlight", curtask.title),
                " day ",
                ("highlight", str(curtask.day_no)),
                " task ",
                ("highlight", str(curtask.task_no)),
            ]
        )
        task_timestamp = urwid.Text(["Generated on ", curtask.timestamp])

        self.download_btn = widget.CMButton("Download")
        urwid.connect_signal(self.download_btn, "click", self._on_download, curtask)

        self._w = urwid.Pile(
            [
                urwid.Text("Today's task"),
                urwid.Padding(task_title, left=2),
                urwid.Padding(task_timestamp, left=2),
                urwid.Divider(),
                button_row([self.download_btn, refresh_btn]),
            ]
        )

    def _on_refresh(self, btn):
        self._activity.async_task(self._fetch_tasks())

    def _on_download(self, btn, taskinfo: soarscore.SoarScoreTaskInfo):
        self._emit("download", taskinfo)


def button_row(buttons):
    return urwid.GridFlow(buttons, 22, 2, 1, "left")

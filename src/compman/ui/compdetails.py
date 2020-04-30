from typing import List, Union, Tuple, cast
import logging
import asyncio

import urwid

from compman import storage
from compman import soaringspot
from compman import xcsoar
from compman.ui import widget
from compman.ui.activity import Activity

nothing = urwid.Pile([])

log = logging.getLogger("compman")

UrwidMarkup = List[Union[str, Tuple[str, str]]]


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

    def create_view(self):
        p2 = lambda w: urwid.Padding(w, left=2)

        self.airspace_group = []
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

        self.waypoint_group = []
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
        return urwid.GridFlow([activate_btn, exit_btn], 22, 2, 1, "left")

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

    async def _update_competition_files(self):
        compurl = self.competition.soaringspot_url
        if compurl is None:
            return

        self.download_status.set_text(("progress", "Refreshing file list..."))
        downloads = await soaringspot.fetch_downloads(compurl)
        new_airspaces, new_waypoints = self._detect_new_files(downloads)

        if not new_airspaces and not new_waypoints:
            self.download_status.set_text(("remark", "No updates"))
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
    ):
        orig_radio = radio.original_widget
        orig_radio.set_label(self._make_label(sf, [("progress", "Downloading...")]))
        dlcontents = await soaringspot.fetch_file(url)
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
        self, sf: storage.StoredFile, extra: UrwidMarkup = None
    ) -> UrwidMarkup:
        label = f"{sf.name} ({sf.format_size()})"
        markup = cast(UrwidMarkup, [label, " "])
        markup.extend(extra or [])
        return markup

    def _make_profile_checkbox(self, profile: str) -> urwid.CheckBox:
        cb = urwid.CheckBox(profile, profile in self.competition.profiles)
        urwid.connect_signal(cb, "change", self._on_profile_changed, profile)
        return urwid.AttrMap(cb, "li normal", "li focus")

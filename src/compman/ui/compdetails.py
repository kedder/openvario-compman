from typing import List
import logging
import asyncio

import urwid

from compman import storage
from compman import soaringspot
from compman import config
from compman.ui import widget

nothing = urwid.Pile([])

log = logging.getLogger("compman")


def logerrors(f):
    async def wrapper(*args, **kwargs):
        try:
            return await f(*args, **kwargs)
        except Exception:
            log.exception("Unexpected exception")

    return wrapper


class CompetitionDetailsScreen:
    def __init__(self, container):
        cid = config.get().current_competition_id
        self.competition = storage.load_competiton(cid)
        self.airspaces = storage.get_airspace_files(cid)
        self.waypoints = storage.get_waypoint_files(cid)
        container.original_widget = self._create_view()

        self._flashtask = None


        self.response = asyncio.Future()
        self._dltask = asyncio.create_task(self._update_competition_files())

    def _create_view(self):
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

        self.download_status = urwid.WidgetPlaceholder(nothing)

        form = urwid.Pile(
            [
                self.download_status,
                urwid.Text("Airspace files"),
                p2(self.airspace_pile),
                urwid.Divider(),
                urwid.Text("Waypoint files"),
                p2(self.waypoint_pile),
                urwid.Divider(),
                self._create_buttons(),
            ]
        )

        filler = urwid.Filler(form, valign=urwid.TOP)

        self.footer = urwid.Text("")

        return urwid.Frame(
            urwid.LineBox(filler, "Details", title_align="left"),
            header=urwid.Text(self.competition.title),
            footer=self.footer,
        )

    def _create_buttons(self):
        apply_btn = widget.CMButton("Apply")
        urwid.connect_signal(apply_btn, "click", self._on_apply)

        exit_btn = widget.CMButton("Main Menu")
        urwid.connect_signal(exit_btn, "click", self._on_exit)
        return urwid.GridFlow([apply_btn, exit_btn], 22, 2, 1, "left")

    def _on_airspace_changed(self, ev, new_state, selected):
        if not new_state:
            return
        self.competition.airspace = selected
        storage.save_competition(self.competition)
        self._flash(f"Airspace changed to: {selected}")

    def _on_waypoint_changed(self, ev, new_state, selected):
        if not new_state:
            return
        self.competition.waypoints = selected
        storage.save_competition(self.competition)
        self._flash(f"Waypoint changed to: {selected}")

    def _on_apply(self, btn):
        self._flash("Settings applied")

    def _on_exit(self, btn):
        self.response.set_result(None)

    def _flash(self, message: str):
        if self._flashtask and not self._flashtask.done():
            self._flashtask.cancel()
        self._flashtask = asyncio.create_task(self._flash_status(message))

    @logerrors
    async def _flash_status(self, message: str):
        self.footer.set_text(message)
        await asyncio.sleep(3.0)
        self.footer.set_text("")

    @logerrors
    async def _update_competition_files(self):
        compurl = self.competition.soaringspot_url
        if compurl is None:
            return

        self.download_status.original_widget = urwid.Text("Downloading file list...")
        downloads = await soaringspot.fetch_downloads(compurl)
        new_airspaces, new_waypoints = self._detect_new_files(downloads)

        if not new_airspaces and not new_waypoints:
            self.download_status.original_widget = nothing
            return

        self.download_status.original_widget = urwid.Text("New contest files detected!")

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
        asyncio.gather(*tasks)

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
            checkbox_pile.contents.insert(0, (radio, ('pack', None)))
            tasks.append(self._download_file(sf, sspotfile.href, radio))

        return tasks

    async def _download_file(
        self, sf: storage.StoredFile, url: str, radio: urwid.RadioButton
    ):
        radio.set_label(self._make_label(sf, ["Downloading..."]))
        dlcontents = await soaringspot.fetch_file(url)
        stored = storage.store_file(self.competition.id, sf.name, dlcontents)
        radio.set_label(self._make_label(stored, ["New!"]))

    def _make_file_radio(
        self, sf: storage.StoredFile, group, selected: bool, select_handler
    ) -> urwid.RadioButton:
        label = f"{sf.name} ({sf.format_size()})"
        radio = urwid.RadioButton(group, label, selected)
        urwid.connect_signal(radio, "change", select_handler, sf.name)
        return radio

    def _make_label(self, sf: storage.StoredFile, extra: List[str] = None) -> List[str]:
        label = f"{sf.name} ({sf.format_size()})"
        return [label, " "] + (extra or [])

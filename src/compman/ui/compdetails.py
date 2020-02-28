import asyncio

import urwid

from compman import storage


class CompetitionDetailsScreen:
    def __init__(self, container, competition: storage.StoredCompetition):
        self.competition = competition
        container.original_widget = self._create_view()
        self.response = asyncio.Future()

        self._flashtask = None

    def _create_view(self):
        airspaces = ["airspace1", "airspace2", "airspace3"]
        waypoints = ["waypoint1", "waypoint2"]

        p2 = lambda w: urwid.Padding(w, left=2)
        airspace_group = []
        airspace_radios = []
        for fname in airspaces:
            radio = urwid.RadioButton(airspace_group, fname)
            urwid.connect_signal(radio, "change", self._on_airspace_changed, fname)
            airspace_radios.append(p2(radio))

        waypoint_group = []
        waypoint_radios = []
        for fname in waypoints:
            radio = urwid.RadioButton(waypoint_group, fname, user_data=fname)
            urwid.connect_signal(radio, "change", self._on_waypoint_changed, fname)
            waypoint_radios.append(p2(radio))

        form = urwid.Pile(
            [urwid.Text("Airspace files")]
            + airspace_radios
            + [urwid.Divider(), urwid.Text("Waypoint files")]
            + waypoint_radios
        )

        filler = urwid.Filler(form, valign=urwid.TOP)

        self.footer = urwid.Text("")

        return urwid.Frame(
            urwid.LineBox(filler, "Details", title_align="left"),
            header=urwid.Text(self.competition.title),
            footer=self.footer,
        )

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

    def _flash(self, message: str):
        if self._flashtask and not self._flashtask.done():
            self._flashtask.cancel()
        self._flashtask = asyncio.create_task(self._flash_status(message))

    async def _flash_status(self, message: str):
        self.footer.set_text(message)
        await asyncio.sleep(3.0)
        self.footer.set_text("")

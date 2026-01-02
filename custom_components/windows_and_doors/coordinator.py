from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .const import CONF_DOORS, CONF_WINDOWS, CONF_SPECIAL

OPEN_STATES = {"on", "open", "opening"}


class WindowsDoorsCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry):
        super().__init__(hass, None, name="Windows and Doors Coordinator")
        self.entry = entry

        self.doors = entry.options.get(CONF_DOORS, entry.data[CONF_DOORS])
        self.windows = entry.options.get(CONF_WINDOWS, entry.data[CONF_WINDOWS])
        self.special = entry.options.get(CONF_SPECIAL, entry.data.get(CONF_SPECIAL, []))

        self.last_door_opened = None
        self.last_door_opened_at = None

    async def async_initialize(self):
        entities = (
            self.doors
            + self.windows
            + [i["entity"] for i in self.special]
        )

        async_track_state_change_event(
            self.hass, entities, self._state_changed
        )

        self.async_set_updated_data(self._collect())

    def restore(self, state):
        if not state:
            return
        self.last_door_opened = state.attributes.get("last_door_opened")
        self.last_door_opened_at = state.attributes.get("door_opened_at")

    def _state_changed(self, event):
        new = event.data.get("new_state")
        if not new:
            return

        if new.entity_id in self.doors and new.state in OPEN_STATES:
            self.last_door_opened = new.name
            self.last_door_opened_at = dt_util.now().isoformat(timespec="seconds")

        self.async_set_updated_data(self._collect())

    def _collect(self):
        open_doors = []
        open_windows = []

        for e in self.doors:
            s = self.hass.states.get(e)
            if s and s.state in OPEN_STATES:
                open_doors.append(s.name)

        for e in self.windows:
            s = self.hass.states.get(e)
            if s and s.state in OPEN_STATES:
                open_windows.append(s.name)

        special_attrs = {}
        for item in self.special:
            key = item["name"].lower().replace(" ", "_")
            s = self.hass.states.get(item["entity"])
            if not s:
                special_attrs[key] = "Unknown"
            elif s.state in OPEN_STATES:
                special_attrs[key] = "Open"
            else:
                special_attrs[key] = "Closed"

        return {
            "number_of_doors": len(open_doors),
            "number_of_windows": len(open_windows),
            "list_of_open": open_doors + open_windows,
            "last_door_opened": self.last_door_opened,
            "door_opened_at": self.last_door_opened_at,
            "all_monitored": {
                "doors": self.doors,
                "windows": self.windows,
                "special_cases": self.special,
            },
            **special_attrs,
        }

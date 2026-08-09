import logging

from homeassistant.core import callback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .const import CONF_DOORS, CONF_WINDOWS, CONF_SPECIAL
from .state_utils import get_entity_status, is_entity_open

_LOGGER = logging.getLogger(__name__)


class WindowsDoorsCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry):
        super().__init__(hass, _LOGGER, name="Windows and Doors Coordinator")
        self.entry = entry

        self.special = entry.options.get(CONF_SPECIAL, entry.data.get(CONF_SPECIAL, []))
        special_entity_ids = {item["entity"] for item in self.special}

        configured_doors = entry.options.get(CONF_DOORS, entry.data[CONF_DOORS])
        configured_windows = entry.options.get(CONF_WINDOWS, entry.data[CONF_WINDOWS])
        self.doors = [entity_id for entity_id in configured_doors if entity_id not in special_entity_ids]
        self.windows = [entity_id for entity_id in configured_windows if entity_id not in special_entity_ids]

        self.last_door_opened = None
        self.last_door_opened_at = None
        self._unsub_state_change = None

    async def async_initialize(self):
        entities = (
            self.doors
            + self.windows
            + [i["entity"] for i in self.special]
        )

        self._unsub_state_change = async_track_state_change_event(
            self.hass, entities, self._state_changed
        )

        self.async_set_updated_data(self._collect())

    def async_stop(self):
        if self._unsub_state_change is not None:
            self._unsub_state_change()
            self._unsub_state_change = None

    def restore(self, state):
        if not state:
            return
        self.last_door_opened = state.attributes.get("last_door_opened")
        self.last_door_opened_at = state.attributes.get("door_opened_at")

    @callback
    def _state_changed(self, event):
        new = event.data.get("new_state")
        if not new:
            return

        if new.entity_id in self.doors and is_entity_open(new.entity_id, new.state):
            self.last_door_opened = new.name
            self.last_door_opened_at = dt_util.now().isoformat(timespec="seconds")

        self.async_set_updated_data(self._collect())

    def _collect(self):
        open_doors = []
        open_windows = []

        for e in self.doors:
            s = self.hass.states.get(e)
            if s and is_entity_open(e, s.state):
                open_doors.append(s.name)

        for e in self.windows:
            s = self.hass.states.get(e)
            if s and is_entity_open(e, s.state):
                open_windows.append(s.name)

        special_attrs = {}
        for item in self.special:
            key = item["name"].lower().replace(" ", "_")
            s = self.hass.states.get(item["entity"])
            special_attrs[key] = get_entity_status(item["entity"], s.state if s else None)

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

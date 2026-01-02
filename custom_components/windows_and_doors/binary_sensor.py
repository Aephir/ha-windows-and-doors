from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN, DATA_COORDINATOR


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    async_add_entities([WindowsDoorsBinarySensor(coordinator, entry)])


class WindowsDoorsBinarySensor(RestoreEntity, BinarySensorEntity):
    _attr_name = "Open doors and windows"
    _attr_device_class = "opening"
    _attr_icon = "custom:windows-and-doors"

    def __init__(self, coordinator, entry):
        self.coordinator = coordinator
        self._attr_unique_id = f"{entry.entry_id}_windows_doors_open"

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        state = await self.async_get_last_state()
        self.coordinator.restore(state)

    @property
    def is_on(self):
        data = self.coordinator.data or {}
        return bool(
            data.get("number_of_doors", 0)
            or data.get("number_of_windows", 0)
        )

    @property
    def extra_state_attributes(self):
        return self.coordinator.data
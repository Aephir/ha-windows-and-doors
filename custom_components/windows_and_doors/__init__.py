from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, DATA_COORDINATOR
from .coordinator import WindowsDoorsCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = WindowsDoorsCoordinator(hass, entry)
    await coordinator.async_initialize()

    entry.runtime_data = {DATA_COORDINATOR: coordinator}
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = entry.runtime_data

    await hass.config_entries.async_forward_entry_setups(
        entry, ["binary_sensor"]
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, ["binary_sensor"]
    )
    if unload_ok:
        coordinator = entry.runtime_data[DATA_COORDINATOR]
        coordinator.async_stop()
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok

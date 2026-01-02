from homeassistant.components.diagnostics import async_redact_data
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN, DATA_COORDINATOR

REDACT_KEYS = []


async def async_get_config_entry_diagnostics(hass, entry):
    registry = er.async_get(hass)
    entities = er.async_entries_for_config_entry(registry, entry.entry_id)

    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]

    return {
        "config": async_redact_data(entry.data, REDACT_KEYS),
        "options": async_redact_data(entry.options, REDACT_KEYS),
        "entities": [
            {
                "entity_id": e.entity_id,
                "unique_id": e.unique_id,
                "platform": e.platform,
            }
            for e in entities
        ],
        "coordinator_data": coordinator.data,
    }

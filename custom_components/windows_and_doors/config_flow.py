from homeassistant import config_entries
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import selector
import voluptuous as vol

from .const import DOMAIN, CONF_DOORS, CONF_WINDOWS, CONF_SPECIAL

CONF_SPECIAL_ENTITIES = "special_entities"
CONF_SPECIAL_NAMES = "special_names"


class WindowsDoorsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def _default_special_items(self, entity_ids):
        items = []
        for entity_id in entity_ids:
            state = self.hass.states.get(entity_id)
            name = state.name if state else entity_id.rsplit(".", 1)[-1].replace("_", " ").title()
            items.append({"entity": entity_id, "name": name})
        return items

    def _entity_selector_config(self, preferred_type=None):
        entity_ids = self._sorted_entity_ids(preferred_type)
        return selector.EntitySelectorConfig(
            domain=["binary_sensor", "cover"],
            multiple=True,
            include_entities=entity_ids,
        )

    def _sorted_entity_ids(self, preferred_type=None):
        registry = er.async_get(self.hass)
        entity_ids = [
            entity_id
            for entity_id in self.hass.states.async_entity_ids()
            if entity_id.split(".", 1)[0] in {"binary_sensor", "cover"}
        ]

        def score(entity_id):
            entry = registry.async_get(entity_id)
            name = ""
            if entry:
                name = (entry.original_name or entry.name or entity_id).lower()
            entity_text = f"{entity_id} {name}".lower()

            if preferred_type == "door":
                if entry and entry.device_class in {"door", "garage_door"}:
                    return (0, entity_id)
                if "door" in entity_text:
                    return (1, entity_id)
                return (2, entity_id)

            if preferred_type == "window":
                if entry and entry.device_class == "window":
                    return (0, entity_id)
                if "window" in entity_text:
                    return (1, entity_id)
                return (2, entity_id)

            return (0, entity_id)

        return [entity_id for entity_id in sorted(entity_ids, key=score)]

    async def async_step_user(self, user_input=None):
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input:
            special_entities = user_input.get(CONF_SPECIAL, [])
            user_input[CONF_SPECIAL] = self._default_special_items(special_entities)
            return self.async_create_entry(
                title="Windows and Doors Summary",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_DOORS): selector.EntitySelector(
                        self._entity_selector_config("door")
                    ),
                    vol.Required(CONF_WINDOWS): selector.EntitySelector(
                        self._entity_selector_config("window")
                    ),
                    vol.Optional(CONF_SPECIAL, default=[]): selector.EntitySelector(
                        self._entity_selector_config()
                    ),
                }
            ),
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        return WindowsDoorsOptionsFlow(config_entry)


class WindowsDoorsOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, entry):
        self.entry = entry
        self.options = dict(entry.options)
        self.data = dict(entry.data)

    async def async_step_init(self, user_input=None):
        return await self.async_step_doors()

    async def async_step_doors(self, user_input=None):
        if user_input:
            self.options[CONF_DOORS] = user_input[CONF_DOORS]
            return await self.async_step_windows()

        return self.async_show_form(
            step_id="doors",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_DOORS,
                        default=self.options.get(
                            CONF_DOORS, self.data.get(CONF_DOORS, [])
                        ),
                    ): selector.EntitySelector(
                        self._entity_selector_config("door")
                    )
                }
            ),
        )

    async def async_step_windows(self, user_input=None):
        if user_input:
            self.options[CONF_WINDOWS] = user_input[CONF_WINDOWS]
            return await self.async_step_special()

        return self.async_show_form(
            step_id="windows",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_WINDOWS,
                        default=self.options.get(
                            CONF_WINDOWS, self.data.get(CONF_WINDOWS, [])
                        ),
                    ): selector.EntitySelector(
                        self._entity_selector_config("window")
                    )
                }
            ),
        )

    async def async_step_special(self, user_input=None):
        if user_input is not None:
            entities = user_input.get(CONF_SPECIAL_ENTITIES, [])
            names = [
                name.strip()
                for name in user_input.get(CONF_SPECIAL_NAMES, "").split(",")
                if name.strip()
            ]

            if len(entities) != len(names):
                return self.async_show_form(
                    step_id="special",
                    errors={"base": "special_count_mismatch"},
                    data_schema=self._special_schema(user_input),
                )

            casefolded_names = [name.casefold() for name in names]
            if len(casefolded_names) != len(set(casefolded_names)):
                return self.async_show_form(
                    step_id="special",
                    errors={"base": "duplicate_names"},
                    data_schema=self._special_schema(user_input),
                )

            self.options[CONF_SPECIAL] = [
                {"entity": entity_id, "name": name}
                for entity_id, name in zip(entities, names)
            ]
            return self.async_create_entry(title="", data=self.options)

        return self.async_show_form(
            step_id="special",
            data_schema=self._special_schema(),
        )

    def _special_schema(self, user_input=None):
        special_items = self.options.get(
            CONF_SPECIAL, self.data.get(CONF_SPECIAL, [])
        )
        default_entities = [item["entity"] for item in special_items]
        default_names = ", ".join(item["name"] for item in special_items)

        if user_input is not None:
            default_entities = user_input.get(
                CONF_SPECIAL_ENTITIES, default_entities
            )
            default_names = user_input.get(
                CONF_SPECIAL_NAMES, default_names
            )

        return vol.Schema(
            {
                vol.Optional(
                    CONF_SPECIAL_ENTITIES,
                    default=default_entities,
                ): selector.EntitySelector(
                    self._entity_selector_config()
                ),
                vol.Optional(
                    CONF_SPECIAL_NAMES,
                    default=default_names,
                ): selector.TextSelector(),
            }
        )

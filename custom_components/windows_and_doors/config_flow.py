from homeassistant import config_entries
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
                        selector.EntitySelectorConfig(
                            domain="binary_sensor", multiple=True
                        )
                    ),
                    vol.Required(CONF_WINDOWS): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="binary_sensor", multiple=True
                        )
                    ),
                    vol.Optional(CONF_SPECIAL, default=[]): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="binary_sensor", multiple=True
                        )
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
                        selector.EntitySelectorConfig(
                            domain="binary_sensor", multiple=True
                        )
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
                        selector.EntitySelectorConfig(
                            domain="binary_sensor", multiple=True
                        )
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
                    selector.EntitySelectorConfig(
                        domain="binary_sensor", multiple=True
                    )
                ),
                vol.Optional(
                    CONF_SPECIAL_NAMES,
                    default=default_names,
                ): selector.TextSelector(),
            }
        )

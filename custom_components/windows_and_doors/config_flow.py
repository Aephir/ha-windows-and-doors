from homeassistant import config_entries
from homeassistant.helpers import selector
import voluptuous as vol

from .const import DOMAIN, CONF_DOORS, CONF_WINDOWS, CONF_SPECIAL


SPECIAL_SCHEMA = vol.Schema(
    {
        vol.Required("entity"): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="binary_sensor")
        ),
        vol.Required("name"): str,
    }
)


class WindowsDoorsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input:
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
                    vol.Optional(CONF_SPECIAL): [SPECIAL_SCHEMA],
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
            names = [i["name"] for i in user_input.get(CONF_SPECIAL, [])]
            if len(names) != len(set(names)):
                return self.async_show_form(
                    step_id="special",
                    errors={"base": "duplicate_names"},
                    data_schema=self._special_schema(),
                )

            self.options[CONF_SPECIAL] = user_input.get(CONF_SPECIAL, [])
            return self.async_create_entry(title="", data=self.options)

        return self.async_show_form(
            step_id="special",
            data_schema=self._special_schema(),
        )

    def _special_schema(self):
        return vol.Schema(
            {
                vol.Optional(
                    CONF_SPECIAL,
                    default=self.options.get(
                        CONF_SPECIAL, self.data.get(CONF_SPECIAL, [])
                    ),
                ): [SPECIAL_SCHEMA]
            }
        )

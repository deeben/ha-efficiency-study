import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_INFLUX_URL,
    CONF_INFLUX_TOKEN,
    CONF_INFLUX_ORG,
    CONF_INFLUX_BUCKET,
    CONF_HOUSE_ID,
    CONF_MONITORED_ENTITIES,
)

CONFIG_SCHEMA = vol.Schema({
    vol.Required(CONF_INFLUX_URL): str,
    vol.Required(CONF_INFLUX_TOKEN): str,
    vol.Required(CONF_INFLUX_ORG): str,
    vol.Required(CONF_INFLUX_BUCKET): str,
    vol.Required(CONF_HOUSE_ID): str,
})

class EfficiencyStudyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Home Efficiency Study."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            # Set the unique ID to the House ID to prevent duplicates
            await self.async_set_unique_id(user_input[CONF_HOUSE_ID])
            self._abort_if_unique_id_configured()
            # Title the entry as the House ID so it shows up named correctly
            return self.async_create_entry(title=user_input[CONF_HOUSE_ID], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=CONFIG_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return EfficiencyStudyOptionsFlowHandler(config_entry)


class EfficiencyStudyOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Create a multi-select entity selector for monitored entities
        # Using the dictionary selector constructor for safer HA version compatibility
        options_schema = vol.Schema({
            vol.Optional(
                CONF_MONITORED_ENTITIES,
                default=self._config_entry.options.get(CONF_MONITORED_ENTITIES, [])
            ): selector.selector({"entity": {"multiple": True}})
        })

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema
        )

import logging
import voluptuous as vol

# from . import ChargingStation
from homeassistant import config_entries
from homeassistant.helpers import config_validation as cv, device_registry as dr

from .const import DOMAIN, CONF_SCAN_INTERVAL, CONF_CHARGING_STATIONS, CONF_UNIQUE_ID, CONF_HOST, CONF_PORT, CONF_ADDRESS

_LOGGER = logging.getLogger(__name__)

class SmartEvseFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Smart EVSE config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        """Initialize the config flow."""
        _LOGGER.info("Kenny : SmartEvseFlowHandler : __init__")
        self.data_schema = vol.Schema({
                vol.Optional(CONF_SCAN_INTERVAL, default=30): cv.positive_int,
                vol.Required(CONF_UNIQUE_ID, default="laadpaal_1_test"): cv.string,
                vol.Required(CONF_HOST, default="10.0.5.19"): cv.string,
                vol.Required(CONF_PORT, default=8888): cv.port,
                vol.Required(CONF_ADDRESS, default=1): cv.positive_int
            })

    async def _show_form(self, errors=None):
        """Show the form to the user."""
        _LOGGER.info("Kenny : SmartEvseFlowHandler : _show_form")
        return self.async_show_form(
            step_id="user", data_schema=self.data_schema, errors=errors or {}
        )

    async def async_step_import(self, import_config):
        """Import a config entry from configuration.yaml."""
        _LOGGER.info("Kenny : SmartEvseFlowHandler : async_step_import : %s", import_config)
        return await self.async_step_user(import_config)

    async def async_step_user(self, user_input=None):
        """Handle the start of the config flow."""
        _LOGGER.info("Kenny : SmartEvseFlowHandler : async_step_user : %s", user_input)
        if not user_input:
            return await self._show_form()

#         await self.async_set_unique_id(user_input[CONF_USERNAME])
#         self._abort_if_unique_id_configured()

#         charging_station = ChargingStation(
#                 user_input[CONF_UNIQUE_ID],
#                 user_input[CONF_HOST],
#                 user_input[CONF_PORT],
#                 user_input[CONF_ADDRESS])
#         charging_station.test_connection

        return self.async_create_entry(
            title="Smart EVSE - {}".format(user_input[CONF_UNIQUE_ID]),
            data=user_input
        )

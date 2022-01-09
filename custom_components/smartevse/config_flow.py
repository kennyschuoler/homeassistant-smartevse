import logging
import voluptuous as vol

# from . import ChargingStation
from homeassistant import config_entries
from homeassistant.helpers import config_validation as cv, device_registry as dr

from .const import DOMAIN, DOMAIN_FRIENDLY, CONF_SCAN_INTERVAL, CONF_CHARGING_STATIONS, CONF_UNIQUE_ID, CONF_FRIENDLY_NAME, CONF_HOST, CONF_PORT, CONF_ADDRESS

_LOGGER = logging.getLogger(__name__)

class SmartEvseFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        self.data_schema = vol.Schema({
                vol.Optional(CONF_SCAN_INTERVAL, default=30): cv.positive_int,
                vol.Required(CONF_UNIQUE_ID, default="laadpaal_1"): cv.string,
                vol.Optional(CONF_FRIENDLY_NAME, default="Laadpaal 1"): cv.string,
                vol.Required(CONF_HOST, default="10.0.5.19"): cv.string,
                vol.Required(CONF_PORT, default=8888): cv.port,
                vol.Required(CONF_ADDRESS, default=1): cv.positive_int
            })

    async def _show_form(self, errors=None):
        return self.async_show_form(
            step_id="user", data_schema=self.data_schema, errors=errors or {}
        )

    async def async_step_import(self, import_config):
        _LOGGER.debug(f"{DOMAIN_FRIENDLY} : Using import configuration to start flow : {import_config}")
        return await self.async_step_user(import_config)

    async def async_step_user(self, user_input=None):
        _LOGGER.debug(f"{DOMAIN_FRIENDLY} : Using user input configuration to start flow : {user_input}")

        if not user_input:
            return await self._show_form()

        if CONF_FRIENDLY_NAME not in user_input:
            user_input[CONF_FRIENDLY_NAME] = user_input[CONF_UNIQUE_ID].replace("_", " ").capitalize()

        return self.async_create_entry(
            title=f"{DOMAIN_FRIENDLY} - {user_input[CONF_FRIENDLY_NAME]}",
            data=user_input
        )

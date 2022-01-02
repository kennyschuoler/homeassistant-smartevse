# -*- coding: utf-8 -*-

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, device_registry
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

# Example configuration :
#
# smartevse:
#   scan_interval: 60
#   charging_stations:
#     - unique_id: laadpaal_1
#       host: 10.0.5.19
#       port: 8888
#       address: 1
#     - unique_id: laadpaal_2
#       host: 10.0.5.19
#       port: 8888
#       address: 2

from homeassistant.const import CONF_SCAN_INTERVAL, CONF_CHARGING_STATIONS, CONF_UNIQUE_ID, CONF_HOST, CONF_PORT, CONF_ADDRESS

DEFAULT_SCAN_INTERVAL=30
DEFAULT_PORT=502
DEFAULT_ADDRESS=1

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.int,
        vol.Required(CONF_CHARGING_STATIONS, default=[]): vol.All(
            cv.ensure_list, [ vol.Schema({
                vol.Optional(CONF_UNIQUE_ID): cv.string,
                vol.Required(CONF_HOST): cv.string,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): cv.port,
                vol.Required(CONF_ADDRESS, default=DEFAULT_ADDRESS): vol.All([vol.Range(min=0, max=255)])
            })
        ])
    })
}, extra=vol.ALLOW_EXTRA)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the component from configuration.yaml."""
    _LOGGER.info("Initiating async setup procedure")
    hass.data.setdefault(DOMAIN, {})

    if hass.config_entries.async_entries(DOMAIN):
        return True

    if DOMAIN not in config:
        return True

    _LOGGER.info("Found Smart EVSE configuration.")
    _LOGGER.info("%s", config[DOMAIN])

    return True

###
### TODO : Initial test script to fetch data
###

# from pymodbus.client.sync import ModbusTcpClient as ModbusClient
# from pymodbus.transaction import ModbusRtuFramer
# from pymodbus.constants import Defaults
#
# HOST='10.0.5.19'
# PORT=8888
# UNIT=0x1
#
# async def fetch_smartevse_data():
#
#     client = ModbusClient(HOST, port=PORT, framer=ModbusRtuFramer)
#     client.connect()
#
#     evse_status = client.read_input_registers(0x0000, 12, unit=UNIT)
#     logging.debug("EVSE Status : %s", evse_status.registers)
#
#     node_specific_config = client.read_input_registers(0x0100, 10, unit=UNIT)
#     logging.debug("Node specific configuration : %s", node_specific_config.registers)
#
#     system_config = client.read_input_registers(0x0200, 25, unit=UNIT)
#     logging.debug("System configuration : %s", system_config.registers)
#
#     client.close()

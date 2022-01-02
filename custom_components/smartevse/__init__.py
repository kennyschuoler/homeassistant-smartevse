# -*- coding: utf-8 -*-

import logging
import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, device_registry
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.transaction import ModbusRtuFramer
from pymodbus.constants import Defaults

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

from homeassistant.const import DOMAIN, CONF_SCAN_INTERVAL, CONF_CHARGING_STATIONS, CONF_UNIQUE_ID, CONF_HOST, CONF_PORT, CONF_ADDRESS

DEFAULT_SCAN_INTERVAL = 30
DEFAULT_PORT = 502
DEFAULT_ADDRESS = 1

CHARGING_STATIONS = vol.Schema({
    vol.Required(CONF_UNIQUE_ID): cv.string,
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_PORT, default=DEFAULT_PORT): cv.port,
    vol.Required(CONF_ADDRESS): vol.All(vol.Range(min=0, max=255))
})

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.All(vol.Schema({
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.positive_int,
        vol.Required(CONF_CHARGING_STATIONS): vol.All(cv.ensure_list, [CHARGING_STATIONS])
    }))
}, extra=vol.ALLOW_EXTRA)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the component from configuration.yaml."""
    _LOGGER.info("Initiating async setup procedure")
    # hass.data.setdefault(DOMAIN, {})

    # if hass.config_entries.async_entries(DOMAIN):
    #     return True

    # if DOMAIN not in config:
    #     return True

    _LOGGER.info("Found Smart EVSE configuration.")
    _LOGGER.info("%s", config[DOMAIN])
    smartevse = config[DOMAIN]

    for charging_station in smartevse[CONF_CHARGING_STATIONS]:
        _LOGGER.info("Configuring charging station %s", charging_station)
        entity = ChargingStation(
                charging_station.get(CONF_UNIQUE_ID),
                charging_station.get(CONF_HOST),
                charging_station.get(CONF_PORT),
                charging_station.get(CONF_ADDRESS))
        entity._fetch_data()

    return True


class ChargingStation:
    def __init__(self, unique_id, host, port, address):
        """Initializing charging station."""
        _LOGGER.info("Initializing charging station with id %s", unique_id)
        self._unique_id = unique_id
        self._host = host
        self._port = port
        self._address = address

    def _fetch_data(self):

        _LOGGER.info("Fetching Smart EVSE charging station data")

        client = ModbusClient(self._host, self._port, framer=ModbusRtuFramer)
        client.connect()

        self._evse_status = client.read_input_registers(0x0000, 12, unit=self._address)
        logging.info("EVSE Status : %s", self._evse_status.registers)

        self._node_specific_config = client.read_input_registers(0x0100, 10, unit=self._address)
        logging.info("Node specific configuration : %s", self._node_specific_config.registers)

        self._system_config = client.read_input_registers(0x0200, 25, unit=self._address)
        logging.info("System configuration : %s", self._system_config.registers)

        client.close()

        return self

# -*- coding: utf-8 -*-

import time
import logging
import voluptuous as vol

from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, device_registry as dr
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator, UpdateFailed
from homeassistant.config_entries import ConfigEntry, SOURCE_IMPORT
from homeassistant.components.sensor import DEVICE_CLASSES, SensorEntity

from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.transaction import ModbusRtuFramer
from pymodbus.constants import Defaults

_LOGGER = logging.getLogger(__name__)

from .const import DOMAIN, DATA_COORDINATOR, CONF_SCAN_INTERVAL, CONF_CHARGING_STATIONS, CONF_UNIQUE_ID, CONF_HOST, CONF_PORT, CONF_ADDRESS

PLATFORMS = ["sensor"]

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

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the component from configuration.yaml."""
    hass.data.setdefault(DOMAIN, {DATA_COORDINATOR: {}})
    # hass.data[DOMAIN] = {DATA_COORDINATOR: {}}

    if hass.config_entries.async_entries(DOMAIN):
        return True

    if DOMAIN not in config:
        _LOGGER.info("Kenny : No Smart EVSE configuration found. Skipping...")
        return True

    _LOGGER.info("Kenny : Found Smart EVSE configuration!")
    smartevse = config[DOMAIN]

    for charging_station in smartevse[CONF_CHARGING_STATIONS]:
        _LOGGER.info("Kenny : Configuring charging station %s", charging_station)

        _LOGGER.info("Kenny : async_setup : Done creating async_register_new_charging_station")

        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": SOURCE_IMPORT},
                data=charging_station,
            )
        )

        _LOGGER.info("Kenny : async_setup : Done creating async_init")

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    _LOGGER.info("Kenny : Async setup entry : %s - %s", entry.entry_id, entry)
    _LOGGER.info("Kenny : Async setup entry data : %s", entry.data)

    charging_station = entry.data

    hass.async_create_task(
        async_register_new_charging_station(hass, charging_station, entry)
    )

    async def async_update():
        _LOGGER.info("Kenny : async_setup_entry : async_update : %s", charging_station)
        updated_charging_station = ChargingStation(charging_station[CONF_UNIQUE_ID], charging_station[CONF_HOST], charging_station[CONF_PORT], charging_station[CONF_ADDRESS])
        return updated_charging_station.async_update_data()

    INTERVAL = timedelta(seconds=30) # TODO change to variable
    coordinator = hass.data[DOMAIN][DATA_COORDINATOR][entry.entry_id] = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="smartevse-{}".format(charging_station[CONF_UNIQUE_ID]),
        update_interval=INTERVAL,
        update_method=async_update,
    )

    await coordinator.async_refresh()
#     await coordinator.async_config_entry_first_refresh()

    for platform in PLATFORMS:
        _LOGGER.info("Kenny : Creating task for platform : %s", platform)
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    return True

async def async_register_new_charging_station(hass: HomeAssistant, charging_station: dict, entry: ConfigEntry):
    """Register a new charging station."""
    _LOGGER.info("Kenny : Initializing async_register_new_charging_station %s", charging_station)
    device_registry = await dr.async_get_registry(hass)
    test = device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, charging_station.get(CONF_UNIQUE_ID))},
        manufacturer="Stegen",
        name="Smart EVSE - {}".format(charging_station.get(CONF_UNIQUE_ID)),
        model="v2.2",
        sw_version="v2.31",
    )

class ChargingStation:
    def __init__(self, unique_id, host, port, address):
        """Initializing charging station."""
        _LOGGER.info("Kenny : Initializing charging station object with id %s", unique_id)
        self._unique_id = unique_id
        self._host = host
        self._port = port
        self._address = address

    @property
    def unique_id(self) -> str:
        return f"{self._unique_id}"

    @property
    def host(self) -> str:
        return f"{self._host}"

    @property
    def port(self) -> str:
        return f"{self._port}"

    @property
    def address(self) -> str:
        return f"{self._address}"

    @property
    def evse_status(self) -> str:
        return f"{self._evse_status}"

    @property
    def node_specific_config(self) -> str:
        return f"{self._node_specific_config}"

    @property
    def system_config(self) -> str:
        return f"{self._system_config}"

    def __repr__(self):
        return "%s(unique_id: %s, host: %s, port: %s, address: %s, evse_status: %s, node_specific_config: %s, system_config: %s)" % (self.__class__.__name__, self._unique_id, self._host, self._port, self._address, self._evse_status, self._node_specific_config, self._system_config)

    async def test_connection(self) -> bool:
        """Test connectivity that the charging station is reachable."""
        _LOGGER.info("Kenny : Testing modbus connection")
        client = ModbusClient(self._host, self._port, framer=ModbusRtuFramer)
        client.connect()
        client.close()
        return True

    async def async_update_data(self) -> bool:
        """Updating data."""
        _LOGGER.info("Kenny : Fetching Smart EVSE charging station data")

        client = ModbusClient(self._host, self._port, framer=ModbusRtuFramer)
        client.connect()

        attempt = 0
        max_retries = 10
        while attempt < max_retries:
            attempt += 1
            try:
                self._evse_status = client.read_input_registers(0x0000, 12, unit=self._address)
                _LOGGER.info("Kenny : Attempt %s : EVSE Status : %s", attempt, self._evse_status.registers)
            except results.isError():
                _LOGGER.error("Kenny : Attempt %s : EVSE Status")
                time.sleep(1)
                continue
            break

        attempt = 0
        max_retries = 10
        while attempt < max_retries:
            attempt += 1
            try:
                self._node_specific_config = client.read_input_registers(0x0100, 10, unit=self._address)
                _LOGGER.info("Kenny : Attempt %s : Node specific configuration : %s", attempt, self._node_specific_config.registers)
            except results.isError():
                _LOGGER.error("Kenny : Attempt %s : Node specific configuration")
                time.sleep(1)
                continue
            break

        attempt = 0
        max_retries = 10
        while attempt < max_retries:
            attempt += 1
            try:
                self._system_config = client.read_input_registers(0x0200, 25, unit=self._address)
                _LOGGER.info("Kenny : Attempt %s : System configuration : %s", attempt, self._system_config.registers)
            except results.isError():
                _LOGGER.error("Kenny : Attempt %s : System configuration")
                time.sleep(1)
                continue
            break

        client.close()

        _LOGGER.error("Kenny : Returning self : %s", self)
        _LOGGER.error("Kenny : Returning self unique_id : %s", self._unique_id)

        return self

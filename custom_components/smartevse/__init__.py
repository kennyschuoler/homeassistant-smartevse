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

from .const import DOMAIN, DOMAIN_FRIENDLY, DEVICE_MANUFACTURER, DATA_COORDINATOR, CONF_SCAN_INTERVAL, CONF_CHARGING_STATIONS, CONF_UNIQUE_ID, CONF_FRIENDLY_NAME, CONF_HOST, CONF_PORT, CONF_ADDRESS

PLATFORMS = ["sensor"]

DEFAULT_SCAN_INTERVAL = 30
DEFAULT_PORT = 502
DEFAULT_ADDRESS = 1

CHARGING_STATIONS = vol.Schema({
    vol.Required(CONF_UNIQUE_ID): cv.string,
    vol.Optional(CONF_FRIENDLY_NAME): cv.string,
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

    if hass.config_entries.async_entries(DOMAIN):
        _LOGGER.debug(f"{DOMAIN_FRIENDLY} : A configuration is already applied. Skipping setup...")
        return True

    if DOMAIN not in config:
        _LOGGER.debug(f"{DOMAIN_FRIENDLY} : No configuration found. Skipping setup...")
        return True

    _LOGGER.info(f"{DOMAIN_FRIENDLY} : Found configuration! Starting installation...")

    for charging_station in config[DOMAIN][CONF_CHARGING_STATIONS]:
        _LOGGER.debug(f"{DOMAIN_FRIENDLY} : Setting up charging station with following config : {charging_station}")
        charging_station[CONF_SCAN_INTERVAL] = config[DOMAIN][CONF_SCAN_INTERVAL]
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": SOURCE_IMPORT},
                data=charging_station,
            )
        )

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    _LOGGER.debug(f"{DOMAIN_FRIENDLY} : Setting up entry with id '{entry.entry_id}' and data '{entry.data}'")

    charging_station = entry.data

    hass.async_create_task(
        async_register_new_charging_station(hass, entry)
    )

    async def async_update():
        charging_station_to_update = ChargingStation(
            charging_station[CONF_UNIQUE_ID],
            charging_station[CONF_FRIENDLY_NAME],
            charging_station[CONF_HOST],
            charging_station[CONF_PORT],
            charging_station[CONF_ADDRESS],
            charging_station[CONF_SCAN_INTERVAL]
        )
        _LOGGER.debug(f"{DOMAIN_FRIENDLY} : Updating sensor values for charging station : {charging_station_to_update}")
        return await charging_station_to_update.async_update_data()

    INTERVAL = timedelta(seconds=int(charging_station[CONF_SCAN_INTERVAL]))
    coordinator = hass.data[DOMAIN][DATA_COORDINATOR][entry.entry_id] = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{DOMAIN}-{charging_station[CONF_UNIQUE_ID]}",
        update_interval=INTERVAL,
        update_method=async_update,
    )

    await coordinator.async_refresh()
#     await coordinator.async_config_entry_first_refresh()

    for platform in PLATFORMS:
        _LOGGER.debug(f"{DOMAIN_FRIENDLY} : Delegating configuration to platform : {platform}")
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    return True

async def async_register_new_charging_station(hass: HomeAssistant, entry: ConfigEntry):
    """Register a new charging station."""
    _LOGGER.debug(f"{DOMAIN_FRIENDLY} : Registering device : {entry.data} with entry id : {entry.entry_id}")
    device_registry = await dr.async_get_registry(hass)
    test = device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.data.get(CONF_UNIQUE_ID))},
        manufacturer=f"{DEVICE_MANUFACTURER}",
        name=f"{DOMAIN_FRIENDLY} - {entry.data.get(CONF_FRIENDLY_NAME)}",
    )

class ChargingStation:
    def __init__(self, unique_id, friendly_name, host, port, address, scan_interval=30):
        """Initializing charging station."""
        self._unique_id = unique_id
        self._friendly_name = friendly_name
        self._host = host
        self._port = port
        self._address = address
        self._scan_interval = scan_interval
        self._evse_status = None
        self._node_specific_config = None
        self._system_config = None

    @property
    def unique_id(self) -> str:
        return f"{self._unique_id}"

    @property
    def friendly_name(self) -> str:
        return f"{self._friendly_name}"

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
    def scan_interval(self) -> timedelta:
        return f"{self._scan_interval}"

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
        return "%s(unique_id: %s, friendly_name: %s, host: %s, port: %s, address: %s, scan_interval: %s, evse_status: %s, node_specific_config: %s, system_config: %s)" % (self.__class__.__name__, self._unique_id, self._friendly_name, self._host, self._port, self._address, self._scan_interval, self._evse_status, self._node_specific_config, self._system_config)

    async def test_connection(self) -> bool:
        """Test connectivity that the charging station is reachable."""
        _LOGGER.debug(f"{DOMAIN_FRIENDLY} : Testing modbus connection for host '{self._host}' and port '{self._port}'")
        client = ModbusClient(self._host, self._port, framer=ModbusRtuFramer)
        client.connect()
        client.close()
        return True

    async def async_update_data(self):
        """Updating sensor states."""
        _LOGGER.debug(f"{DOMAIN_FRIENDLY} : Fetching latest sensor states for charging station")

        client = ModbusClient(self._host, self._port, framer=ModbusRtuFramer)
        client.connect()

        result = None
        attempt = 0
        max_retries = 10
        succeeded = False
        while attempt < max_retries:
            attempt += 1
            _LOGGER.debug(f"{DOMAIN_FRIENDLY} : Attempt {attempt} to fetch 'EVSE Status'")
            result = client.read_input_registers(0x0000, 12, unit=self._address)
            if result.isError():
                _LOGGER.debug(f"{DOMAIN_FRIENDLY} : Attempt {attempt} failed to fetch 'EVSE Status'")
                time.sleep(attempt)
                succeeded = True
                continue
            else:
                self._evse_status = result.registers
                break
        if not succeeded:
            _LOGGER.error(f"{DOMAIN_FRIENDLY} : Failed to fetch 'EVSE Status' (tried {attempt} times)")

        result = None
        attempt = 0
        max_retries = 10
        succeeded = False
        while attempt < max_retries:
            attempt += 1
            _LOGGER.debug(f"{DOMAIN_FRIENDLY} : Attempt {attempt} to fetch 'Node specific configuration'")
            result = client.read_input_registers(0x0100, 10, unit=self._address)
            if result.isError():
                _LOGGER.debug(f"{DOMAIN_FRIENDLY} : Attempt {attempt} failed to fetch 'Node specific configuration'")
                time.sleep(attempt)
                succeeded = True
                continue
            else:
                self._node_specific_config = result.registers
                break
        if not succeeded:
            _LOGGER.error(f"{DOMAIN_FRIENDLY} : Failed to fetch 'Node specific configuration' (tried {attempt} times)")

        result = None
        attempt = 0
        max_retries = 10
        succeeded = False
        while attempt < max_retries:
            attempt += 1
            _LOGGER.debug(f"{DOMAIN_FRIENDLY} : Attempt {attempt} to fetch 'System configuration'")
            result = client.read_input_registers(0x0200, 25, unit=self._address)
            if result.isError():
                _LOGGER.debug(f"{DOMAIN_FRIENDLY} : Attempt {attempt} failed to fetch 'System configuration'")
                time.sleep(attempt)
                succeeded = True
                continue
            else:
                self._system_config = result.registers
                break
        if not succeeded:
            _LOGGER.error(f"{DOMAIN_FRIENDLY} : Failed to fetch 'System configuration' (tried {attempt} times)")

        client.close()

        return {
            "_evse_status": self._evse_status,
            "_node_specific_config": self._node_specific_config,
            "_system_config": self._system_config
        }

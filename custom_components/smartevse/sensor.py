import logging

from typing import Callable
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import DEVICE_CLASSES, SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN, DATA_COORDINATOR, CONF_UNIQUE_ID

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: Callable):
    """Config entry example."""
    _LOGGER.info("Kenny : Setting up entry : %s", entry)
    _LOGGER.info("Kenny : Setting up entry data : %s", entry.data)

#     data = hass.data[DOMAIN][entry.entry_id][DATA]
#     coordinator = data.coordinator

    coordinator = hass.data[DOMAIN][DATA_COORDINATOR][entry.entry_id]

    _LOGGER.info("Kenny : Using coordinator : %s", coordinator)
    _LOGGER.info("Kenny : Using coordinator data : %s", coordinator.data)

    if not coordinator.data:
        _LOGGER.info("Kenny : No coordinator data !")
        return

    sensor_list = []

    # 0 = State
    # 1 = Error
    # 2 = Charging current
    # 3 = EVSE mode (without saving)
    # 4 = Solar Timer
    # 5 = Access bit
    # 6 = Configuration changed (Not implemented)
    # 7 = Maximum charging current
    # 8 = Number of used phases (Not implemented)
    # 9 = Real charging current (Not implemented)
    # 10 = Temperature
    # 11 = Serial number

    evse_status = [ 1, 2, 3 ]

    sensor_list.append(SmartEvseSensor(coordinator, DOMAIN, entry.data[CONF_UNIQUE_ID], "state", "State", evse_status[0], None, None))
    sensor_list.append(SmartEvseSensor(coordinator, DOMAIN, entry.data[CONF_UNIQUE_ID], "error", "Error", evse_status[1], None, None))
    sensor_list.append(SmartEvseSensor(coordinator, DOMAIN, entry.data[CONF_UNIQUE_ID], "charging_current", "Charging current", evse_status[2], None, None))
#
#     node_specific_config = getattr(coordinator.data, "node_specific_config")
#     system_config = getattr(coordinator.data, "system_config")
#
    async_add_entities(sensor_list)

class SmartEvseSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Smart EVSE Sensor."""

    def __init__(self, coordinator, domain, unique_id, sensor_id, sensor_name, sensor_value, device_class, unit_of_measurement):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self._domain = domain
        self._unique_id = unique_id
        self._sensor_id = sensor_id
        self._sensor_name = sensor_name
        self._sensor_value = sensor_value
        self._device_class = device_class
        self._unit_of_measurement = unit_of_measurement

    @property
    def unique_id(self) -> str:
        """Return a unique, unchanging string that represents this entity."""
        return f'{self._domain}_{self._unique_id}_{self._sensor_id}'

    @property
    def name(self) -> str:
        """Return the name."""
        return f"Smart EVSE - {self._unique_id} - {self._sensor_name}"

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        return self._sensor_value

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def device_class(self) -> str:
        """Return the device class."""
        return self._device_class

    @property
    def state_class(self) -> str:
        """Return the state_class for the sensor, to enable statistics"""
        return None

    @property
    def device_info(self) -> dict:
        """Return device registry information for this entity."""

#             "name": f"Smart EVSE - {self._unique_id}",
#         "name": f"{self._sensor_name} Sensor",
#             "identifiers": {(self._domain, self._unique_id, self._sensor_id)},
        return {
            "identifiers": {(self._domain, self._unique_id)},
            "via_device": (self._domain, self._unique_id)
        }


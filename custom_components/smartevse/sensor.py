import logging

from typing import Callable
from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import DEVICE_CLASSES, SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN, DOMAIN_FRIENDLY, DATA_COORDINATOR, CONF_UNIQUE_ID, CONF_FRIENDLY_NAME

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: Callable):
#     data = hass.data[DOMAIN][entry.entry_id][DATA]
#     coordinator = data.coordinator

    coordinator = hass.data[DOMAIN][DATA_COORDINATOR][entry.entry_id]

    if not coordinator.data:
        _LOGGER.debug(f"{DOMAIN_FRIENDLY} : No coordinator data available to continue sensor configuration")
        return

    sensor_list = []

    sensor_list.append(SmartEvseSensor(coordinator, entry.data, "State", "_evse_status", 0, None, None))
    sensor_list.append(SmartEvseSensor(coordinator, entry.data, "Error", "_evse_status", 1, None, None))
    sensor_list.append(SmartEvseSensor(coordinator, entry.data, "Charging current", "_evse_status", 2, None, None))
    sensor_list.append(SmartEvseSensor(coordinator, entry.data, "EVSE mode (without saving)", "_evse_status", 3, None, None))
    sensor_list.append(SmartEvseSensor(coordinator, entry.data, "Solar Timer", "_evse_status", 4, None, None))
    sensor_list.append(SmartEvseSensor(coordinator, entry.data, "Access bit", "_evse_status", 5, None, None))
#     sensor_list.append(SmartEvseSensor(coordinator, entry.data, "Configuration changed (Not implemented)", "_evse_status", 6, None, None))
    sensor_list.append(SmartEvseSensor(coordinator, entry.data, "Maximum charging current", "_evse_status", 7, None, None))
#     sensor_list.append(SmartEvseSensor(coordinator, entry.data, "Number of used phases (Not implemented)", "_evse_status", 8, None, None))
#     sensor_list.append(SmartEvseSensor(coordinator, entry.data, "Real charging current (Not implemented)", "_evse_status", 9, None, None))
    sensor_list.append(SmartEvseSensor(coordinator, entry.data, "Temperature", "_evse_status", 10, None, None))
    sensor_list.append(SmartEvseSensor(coordinator, entry.data, "Serial number", "_evse_status", 11, None, None))

#     node_specific_config = getattr(coordinator.data, "node_specific_config")
#     system_config = getattr(coordinator.data, "system_config")

    async_add_entities(sensor_list)

class SmartEvseSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Smart EVSE Sensor."""

    def __init__(self, coordinator, charging_station, sensor_name, sensor_value_category_key, sensor_value_item_key, device_class, unit_of_measurement):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self._charging_station = charging_station
        self._sensor_name = sensor_name
        self._sensor_value_category_key = sensor_value_category_key
        self._sensor_value_item_key = sensor_value_item_key
        self._sensor_value = None
        self._device_class = device_class
        self._unit_of_measurement = unit_of_measurement

    @property
    def unique_id(self) -> str:
        """Return a unique, unchanging string that represents this entity."""
        sensor_id = self._sensor_name.replace("(", "").replace(")", "").replace(" - ", " ").replace(" ", "_").lower()
        return f'{DOMAIN}_{self._charging_station[CONF_UNIQUE_ID]}_{sensor_id}'

    @property
    def name(self) -> str:
        """Return the name."""
        return f"{DOMAIN_FRIENDLY} - {self._charging_station[CONF_FRIENDLY_NAME]} {self._sensor_name}"

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        return self._sensor_value

    @callback
    def _async_update_from_latest_data(self) -> None:
        """Fetch new state data for the sensor."""
        if self._sensor_value_category_key in self.coordinator.data:
            category = self.coordinator.data[self._sensor_value_category_key]
            if 0 <= self._sensor_value_item_key < len(category):
                new_sensor_value = category[self._sensor_value_item_key]
                _LOGGER.debug(f"{DOMAIN_FRIENDLY} : Updating sensor value from {self._sensor_value} to {new_sensor_value}")
                self._sensor_value = new_sensor_value
            else:
                _LOGGER.warn(f"{DOMAIN_FRIENDLY} : Index '{self._sensor_value_item_key}' in category '{self._sensor_value_category_key}' is not defined")
        else:
            _LOGGER.warn(f"{DOMAIN_FRIENDLY} : Category key '{self._sensor_value_category_key}' not defined")


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

        return {
            "identifiers": {(DOMAIN, self._charging_station[CONF_UNIQUE_ID])},
            "via_device": (DOMAIN, self._charging_station[CONF_UNIQUE_ID])
        }

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""

        @callback
        def update():
            """Update the state."""
            self._async_update_from_latest_data()
            self.async_write_ha_state()

        self.async_on_remove(self.coordinator.async_add_listener(update))

        self._async_update_from_latest_data()
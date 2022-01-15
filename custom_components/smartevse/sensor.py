import logging

from typing import Callable, Optional
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

    # Device classes : https://www.home-assistant.io/integrations/sensor/
    sensor_list.append(SmartEvseSensor(coordinator, entry.data, "State", "_evse_status", 0, None, None, {}, {}))
    sensor_list.append(SmartEvseSensor(coordinator, entry.data, "Error", "_evse_status", 1, None, None, {}, { "0": "", "1": "LESS_6A", "2": "NO_COMM", "4": "TEMP_HIGH", "8": "Unused", "16": "RCD", "32": "NO_SUN" }))
    sensor_list.append(SmartEvseSensor(coordinator, entry.data, "Charging current", "_evse_status", 2, "A", "current", { "precision": 1 }, {}))
    sensor_list.append(SmartEvseSensor(coordinator, entry.data, "EVSE mode (without saving)", "_evse_status", 3, None, None, {}, { "0": "Normal", "1": "Smart", "2": "Solar" }))
    sensor_list.append(SmartEvseSensor(coordinator, entry.data, "Solar Timer", "_evse_status", 4, "s", None, {}, {}))
    sensor_list.append(SmartEvseSensor(coordinator, entry.data, "Access bit", "_evse_status", 5, None, None, {}, { "0": "No Access", "1": "Access" }))
#     sensor_list.append(SmartEvseSensor(coordinator, entry.data, "Configuration changed (Not implemented)", "_evse_status", 6, None, None, {}, {}))
    sensor_list.append(SmartEvseSensor(coordinator, entry.data, "Maximum charging current", "_evse_status", 7, "A", "current", {}, {}))
#     sensor_list.append(SmartEvseSensor(coordinator, entry.data, "Number of used phases (Not implemented)", "_evse_status", 8, None, None, {}, {}))
#     sensor_list.append(SmartEvseSensor(coordinator, entry.data, "Real charging current (Not implemented)", "_evse_status", 9, "A", "current", {}, {}))
    sensor_list.append(SmartEvseSensor(coordinator, entry.data, "Temperature", "_evse_status", 10, "°C", "temperature",  { "offset": "-273.16" }, {}))
    sensor_list.append(SmartEvseSensor(coordinator, entry.data, "Serial number", "_evse_status", 11, None, None, {}, {}))

    sensor_list.append(SmartEvseSensor(coordinator, entry.data, "Configuration", "_node_specific_config", 0, None, None, {}, { "0": "Socket", "1": "Fixed Cable" }))
    sensor_list.append(SmartEvseSensor(coordinator, entry.data, "Cable lock", "_node_specific_config", 1, None, None, {}, { "0": "Disable", "1": "Solenoid", "2": "Motor" }))
    sensor_list.append(SmartEvseSensor(coordinator, entry.data, "MIN Charge Current the EV will accept", "_node_specific_config", 2, "A", "current", {}, {}))
    sensor_list.append(SmartEvseSensor(coordinator, entry.data, "MAX Charge Current for this EVSE", "_node_specific_config", 3, "A", "current", {}, {}))
    sensor_list.append(SmartEvseSensor(coordinator, entry.data, "Load Balance", "_node_specific_config", 4, None, None, {}, { "0": "Disabled", "1": "Master" }))
    sensor_list.append(SmartEvseSensor(coordinator, entry.data, "External Switch on pin SW", "_node_specific_config", 5, None, None, {}, { "0": "Disabled", "1": "Access Push-Button", "2": "Access Switch", "3": "Smart-Solar Push-Button", "4": "Smart-Solar Switch" }))
    sensor_list.append(SmartEvseSensor(coordinator, entry.data, "Residual Current Monitor on pin RCM", "_node_specific_config", 6, None, None, {}, { "0": "Disabled", "1": "Enabled" }))
    sensor_list.append(SmartEvseSensor(coordinator, entry.data, "Use RFID reader", "_node_specific_config", 7, None, None, {}, { "0": "Disabled", "1": "Enabled" }))
    sensor_list.append(SmartEvseSensor(coordinator, entry.data, "Type of EV electric meter", "_node_specific_config", 8, None, None, {}, {}))
#     sensor_list.append(SmartEvseSensor(coordinator, entry.data, "Address of EV electric meter", "_node_specific_config", 9, None, None, {}, {}))

    sensor_list.append(SmartEvseSensor(coordinator, entry.data, "EVSE mode", "_system_config", 0, None, None, {}, { "0": "Normal", "1": "Smart", "2": "Solar" }))
    sensor_list.append(SmartEvseSensor(coordinator, entry.data, "EVSE Circuit max Current", "_system_config", 1, "A", "current", {}, {}))
    sensor_list.append(SmartEvseSensor(coordinator, entry.data, "Grid type to which the Sensorbox is connected", "_system_config", 2, None, None, {}, { "0": "4-Wire", "1": "3-Wire" }))
    sensor_list.append(SmartEvseSensor(coordinator, entry.data, "CT calibration value", "_system_config", 3, None, None, { "precision": 2 }, {}))
    sensor_list.append(SmartEvseSensor(coordinator, entry.data, "Max Mains Current", "_system_config", 4, "A", "current", {}, {}))
    sensor_list.append(SmartEvseSensor(coordinator, entry.data, "Surplus energy start Current", "_system_config", 5, "A", "current", {}, {}))
    sensor_list.append(SmartEvseSensor(coordinator, entry.data, "Stop solar charging at 6A after this time	", "_system_config", 6, "min", None, {}, {}))
    sensor_list.append(SmartEvseSensor(coordinator, entry.data, "Allow grid power when solar charging", "_system_config", 7, "A", "current", {}, {}))
    sensor_list.append(SmartEvseSensor(coordinator, entry.data, "Type of Mains electric meter", "_system_config", 8, None, None, {}, {}))
#     sensor_list.append(SmartEvseSensor(coordinator, entry.data, "Address of Mains electric meter", "_system_config", 9, None, None, {}, {}))
    sensor_list.append(SmartEvseSensor(coordinator, entry.data, "What does Mains electric meter measure", "_system_config", 10, None, None, {}, { "0": "Mains (Home + EVSE + PV)", "1": "Home + EVSE" }))

    async_add_entities(sensor_list)

class SmartEvseSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Smart EVSE Sensor."""

    def __init__(self, coordinator, charging_station, sensor_name, sensor_value_category_key, sensor_value_item_key, unit_of_measurement, device_class, properties={}, friendly_sensor_values={}):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self._charging_station = charging_station
        self._sensor_name = sensor_name
        self._sensor_value_category_key = sensor_value_category_key
        self._sensor_value_item_key = sensor_value_item_key
        self._sensor_value = None
        self._device_class = device_class
        self._unit_of_measurement = unit_of_measurement
        self._properties = properties
        self._friendly_sensor_values = friendly_sensor_values

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
                new_sensor_value = round(category[self._sensor_value_item_key] + self.offset(), self.precision())
                if str(new_sensor_value) in self._friendly_sensor_values:
                    new_sensor_value = self._friendly_sensor_values[str(new_sensor_value)]
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
    def state_class(self) -> Optional[str]:
        """Return the state_class for the sensor, to enable statistics"""
        if not self._device_class:
            return None
        return "measurement"

    def offset(self) -> float:
        if "offset" in self._properties:
            return float(self._properties["offset"])
        return 0

    def precision(self) -> int:
        if "precision" in self._properties:
            return int(self._properties["precision"])
        return 0

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
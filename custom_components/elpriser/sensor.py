# sensor.py
from datetime import timedelta
import logging
import aiohttp
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
from .const import DOMAIN, PRICE_AREAS

LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    try:
        config_data = hass.data[DOMAIN][config_entry.entry_id]
        område = config_data["område"]
        update_interval = config_data["update_interval"]

        async def async_fetch_data():
            """Fetch data from API."""
            url = f"https://henrikhjelm.se/api/elpriset.php?område={område}"
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            return await response.json()
                        LOGGER.error(f"API returned status {response.status}")
                        return None
            except Exception as e:
                LOGGER.error(f"Error fetching data: {str(e)}")
                return None

        coordinator = DataUpdateCoordinator(
            hass,
            LOGGER,
            name=DOMAIN,
            update_method=async_fetch_data,
            update_interval=timedelta(minutes=update_interval),
        )

        await coordinator.async_config_entry_first_refresh()

        sensors = [
            ElprisPriceSensor(coordinator, "current_price", "Nuvarande Pris"),
            ElprisPriceSensor(coordinator, "max_price", "Högsta Pris"),
            ElprisPriceSensor(coordinator, "min_price", "Lägsta Pris"),
            ElprisPriceSensor(coordinator, "average_price", "Genomsnittspris"),
            ElprisPriceSensor(coordinator, "next_hour_price", "Nästa Timmes Pris"),
            ElprisPriceSensor(coordinator, "previous_hour_price", "Föregående Timmes Pris"),
            ElprisTextSensor(coordinator, "price_trend", "Pristrend"),
            ElprisTextSensor(coordinator, "tid", "Aktuell Tidsperiod"),
            ElprisTextSensor(coordinator, "lowest_price_hour", "Billigaste Timmen"),
            ElprisTextSensor(coordinator, "highest_price_hour", "Dyraste Timmen"),
            ElprisTextSensor(coordinator, "best_charging_period.start_time", "Bästa Laddperiod Start"),
            ElprisNumberSensor(coordinator, "best_charging_period.duration", "Bästa Laddperiod Längd", "h"),
            ElprisPriceSensor(coordinator, "best_charging_period.average_price", "Bästa Laddperiod Snittpris"),
        ]

        async_add_entities(sensors)

    except Exception as e:
        LOGGER.error(f"Error setting up sensors: {str(e)}")
        raise

class ElprisPriceSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Price Sensor."""

    def __init__(self, coordinator, sensor_type, name):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._name = name
        self._attr_unique_id = f"{DOMAIN}_{sensor_type}"
        self._attr_native_unit_of_measurement = "kr/kWh"
        self._attr_device_class = SensorDeviceClass.MONETARY
        self._attr_state_class = SensorStateClass.TOTAL
        self._attr_suggested_display_precision = 3

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        
        # Hantera nästlade värden (t.ex. best_charging_period.average_price)
        keys = self._sensor_type.split('.')
        value = self.coordinator.data
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return float(value) if value is not None else None

class ElprisTextSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Text Sensor."""

    def __init__(self, coordinator, sensor_type, name):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._name = name
        self._attr_unique_id = f"{DOMAIN}_{sensor_type}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        
        keys = self._sensor_type.split('.')
        value = self.coordinator.data
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return str(value) if value is not None else None

class ElprisNumberSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Number Sensor."""

    def __init__(self, coordinator, sensor_type, name, unit):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._name = name
        self._attr_unique_id = f"{DOMAIN}_{sensor_type}"
        self._attr_native_unit_of_measurement = unit
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        
        keys = self._sensor_type.split('.')
        value = self.coordinator.data
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return float(value) if value is not None else None
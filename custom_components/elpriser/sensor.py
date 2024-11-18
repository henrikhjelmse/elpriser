# sensor.py
from datetime import timedelta
import logging
import aiohttp
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
from .const import DOMAIN

LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    try:
        # Hämta konfigurationsdata
        config_data = hass.data[DOMAIN][config_entry.entry_id]
        område = config_data["område"]
        update_interval = config_data["update_interval"]

        LOGGER.debug(f"Setting up sensors for område: {område}")

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

        # Fetch initial data
        await coordinator.async_config_entry_first_refresh()

        sensors = [
            ElprisSensor(coordinator, "current_price", "Nuvarande Pris"),
            ElprisSensor(coordinator, "max_price", "Högsta Pris"),
            ElprisSensor(coordinator, "min_price", "Lägsta Pris"),
        ]

        async_add_entities(sensors)
        LOGGER.debug(f"Added {len(sensors)} sensors")

    except Exception as e:
        LOGGER.error(f"Error setting up sensors: {str(e)}")
        raise

class ElprisSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator, sensor_type, name):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._name = name
        self._attr_unique_id = f"{DOMAIN}_{sensor_type}"
        self._attr_native_unit_of_measurement = "kr/kWh"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._sensor_type)
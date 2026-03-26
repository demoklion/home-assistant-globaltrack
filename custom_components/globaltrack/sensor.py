"""Sensor platform for the GlobalTrack integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfElectricPotential,
    UnitOfLength,
    UnitOfSpeed,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import VehicleData
from .const import DOMAIN
from .coordinator import GlobalTrackCoordinator
from .entity import GlobalTrackEntity


@dataclass(frozen=True, kw_only=True)
class GlobalTrackSensorEntityDescription(SensorEntityDescription):
    """Describe a GlobalTrack sensor."""

    value_fn: Callable[[VehicleData], Any]
    extra_attrs_fn: Callable[[VehicleData], dict[str, Any]] | None = None


SENSOR_DESCRIPTIONS: tuple[GlobalTrackSensorEntityDescription, ...] = (
    GlobalTrackSensorEntityDescription(
        key="battery_voltage",
        translation_key="battery_voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda v: v.battery_voltage,
    ),
    GlobalTrackSensorEntityDescription(
        key="odometer",
        translation_key="odometer",
        device_class=SensorDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:counter",
        value_fn=lambda v: v.odometer,
    ),
    GlobalTrackSensorEntityDescription(
        key="speed",
        translation_key="speed",
        device_class=SensorDeviceClass.SPEED,
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda v: v.speed,
    ),
    GlobalTrackSensorEntityDescription(
        key="address",
        translation_key="address",
        icon="mdi:map-marker",
        value_fn=lambda v: v.address,
        extra_attrs_fn=lambda v: {
            "position_timestamp": v.position_timestamp,
            "status_timestamp": v.status_timestamp,
            "ride_timestamp": v.ride_timestamp,
        },
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up GlobalTrack sensors from a config entry."""
    coordinator: GlobalTrackCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        GlobalTrackSensor(coordinator, vehicle_id, description)
        for vehicle_id in coordinator.data
        for description in SENSOR_DESCRIPTIONS
    )


class GlobalTrackSensor(GlobalTrackEntity, SensorEntity):
    """Represent a GlobalTrack sensor."""

    entity_description: GlobalTrackSensorEntityDescription

    def __init__(
        self,
        coordinator: GlobalTrackCoordinator,
        vehicle_id: int,
        description: GlobalTrackSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, vehicle_id)
        self.entity_description = description
        self._attr_unique_id = f"{vehicle_id}_{description.key}"

    @property
    def native_value(self) -> Any:
        """Return the sensor value."""
        return self.entity_description.value_fn(self.vehicle)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra state attributes."""
        if self.entity_description.extra_attrs_fn is not None:
            return self.entity_description.extra_attrs_fn(self.vehicle)
        return None

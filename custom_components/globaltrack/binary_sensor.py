"""Binary sensor platform for the GlobalTrack integration."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import GlobalTrackCoordinator
from .entity import GlobalTrackEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up GlobalTrack binary sensors from a config entry."""
    coordinator: GlobalTrackCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        GlobalTrackIgnitionSensor(coordinator, vehicle_id)
        for vehicle_id in coordinator.data
    )


class GlobalTrackIgnitionSensor(GlobalTrackEntity, BinarySensorEntity):
    """Represent the ignition state of a GlobalTrack vehicle."""

    _attr_device_class = BinarySensorDeviceClass.POWER
    _attr_icon = "mdi:engine"
    _attr_translation_key = "ignition"

    def __init__(
        self, coordinator: GlobalTrackCoordinator, vehicle_id: int
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, vehicle_id)
        self._attr_unique_id = f"{vehicle_id}_ignition"

    @property
    def is_on(self) -> bool | None:
        """Return true if ignition is on."""
        vehicle = self.vehicle
        return vehicle.ignition if vehicle is not None else None

"""Device tracker platform for the GlobalTrack integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.device_tracker import SourceType, TrackerEntity
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
    """Set up GlobalTrack device trackers from a config entry."""
    coordinator: GlobalTrackCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        GlobalTrackDeviceTracker(coordinator, vehicle_id)
        for vehicle_id in coordinator.data
    )


class GlobalTrackDeviceTracker(GlobalTrackEntity, TrackerEntity):
    """Represent a GlobalTrack vehicle on the map."""

    _attr_icon = "mdi:car"

    def __init__(
        self, coordinator: GlobalTrackCoordinator, vehicle_id: int
    ) -> None:
        """Initialize the device tracker."""
        super().__init__(coordinator, vehicle_id)
        self._attr_unique_id = f"{vehicle_id}_tracker"

    @property
    def source_type(self) -> SourceType:
        """Return the source type."""
        return SourceType.GPS

    @property
    def latitude(self) -> float | None:
        """Return latitude value of the device."""
        return self.vehicle.latitude

    @property
    def longitude(self) -> float | None:
        """Return longitude value of the device."""
        return self.vehicle.longitude

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        vehicle = self.vehicle
        return {
            "address": vehicle.address,
            "altitude": vehicle.altitude,
            "speed": vehicle.speed,
            "heading": vehicle.heading,
            "plate": vehicle.plate,
        }

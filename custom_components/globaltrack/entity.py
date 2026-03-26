"""Base entity for the GlobalTrack integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import VehicleData
from .const import DOMAIN
from .coordinator import GlobalTrackCoordinator


class GlobalTrackEntity(CoordinatorEntity[GlobalTrackCoordinator]):
    """Base class for GlobalTrack entities."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: GlobalTrackCoordinator, vehicle_id: int
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._vehicle_id = vehicle_id

    @property
    def vehicle(self) -> VehicleData:
        """Return the vehicle data for this entity."""
        return self.coordinator.data[self._vehicle_id]

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info for this vehicle."""
        vehicle = self.vehicle
        # Vehicle name format is "Model,Driver Name" — use only the first part.
        name = vehicle.name.split(",")[0].strip() if vehicle.name else "Unknown Vehicle"

        return DeviceInfo(
            identifiers={(DOMAIN, str(self._vehicle_id))},
            name=name,
            model=vehicle.kind or None,
            serial_number=vehicle.vin or None,
            manufacturer="GlobalTrack",
        )

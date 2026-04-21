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
    def available(self) -> bool:
        """Return True if the coordinator has fresh data for this vehicle."""
        return (
            super().available
            and self.coordinator.data is not None
            and self._vehicle_id in self.coordinator.data
        )

    @property
    def vehicle(self) -> VehicleData | None:
        """Return the vehicle data for this entity, or None if unavailable."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._vehicle_id)

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info for this vehicle."""
        vehicle = self.vehicle
        name = "Unknown Vehicle"
        model: str | None = None
        serial: str | None = None
        if vehicle is not None:
            # Vehicle name format is "Model,Driver Name" — use only the first part.
            if vehicle.name:
                name = vehicle.name.split(",")[0].strip()
            model = vehicle.kind or None
            serial = vehicle.vin or None

        return DeviceInfo(
            identifiers={(DOMAIN, str(self._vehicle_id))},
            name=name,
            model=model,
            serial_number=serial,
            manufacturer="GlobalTrack",
        )

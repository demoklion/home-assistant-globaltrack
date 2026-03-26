"""DataUpdateCoordinator for the GlobalTrack integration."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    GlobalTrackApi,
    GlobalTrackApiError,
    GlobalTrackAuthError,
    GlobalTrackConnectionError,
    VehicleData,
)
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class GlobalTrackCoordinator(DataUpdateCoordinator[dict[int, VehicleData]]):
    """Coordinator to fetch vehicle data from GlobalTrack."""

    def __init__(self, hass: HomeAssistant, api: GlobalTrackApi) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.api = api

    async def _async_update_data(self) -> dict[int, VehicleData]:
        """Fetch vehicle data from the API."""
        try:
            vehicles = await self.api.async_get_vehicles()
        except GlobalTrackAuthError as err:
            raise ConfigEntryAuthFailed(
                "Authentication failed; please re-authenticate"
            ) from err
        except (GlobalTrackConnectionError, GlobalTrackApiError) as err:
            raise UpdateFailed(f"Error communicating with GlobalTrack: {err}") from err

        return {vehicle.id: vehicle for vehicle in vehicles}

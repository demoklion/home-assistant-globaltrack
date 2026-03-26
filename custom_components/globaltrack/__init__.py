"""GlobalTrack integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import GlobalTrackApi, GlobalTrackAuthError, GlobalTrackConnectionError
from .const import CONF_BASE_URL, DEFAULT_BASE_URL, DOMAIN
from .coordinator import GlobalTrackCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.DEVICE_TRACKER,
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up GlobalTrack from a config entry."""
    session = async_get_clientsession(hass)
    api = GlobalTrackApi(
        session=session,
        base_url=entry.data.get(CONF_BASE_URL, DEFAULT_BASE_URL),
        username=entry.data[CONF_USERNAME],
        password=entry.data[CONF_PASSWORD],
    )

    try:
        await api.authenticate()
    except GlobalTrackAuthError as err:
        raise ConfigEntryAuthFailed(
            "Invalid credentials for GlobalTrack"
        ) from err
    except GlobalTrackConnectionError as err:
        raise ConfigEntryNotReady(
            "Cannot connect to GlobalTrack"
        ) from err

    coordinator = GlobalTrackCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a GlobalTrack config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

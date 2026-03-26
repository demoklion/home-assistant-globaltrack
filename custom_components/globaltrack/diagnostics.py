"""Diagnostics support for the GlobalTrack integration."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

REDACT_KEYS = {
    "username",
    "password",
    "ft_session",
    "clientname",
    "drivername",
    "email",
    "mobile",
    "plate",
    "vin",
    "address",
    "name",
}


def _redact(data: Any) -> Any:
    """Recursively redact sensitive fields."""
    if isinstance(data, dict):
        return {
            k: "**REDACTED**" if k in REDACT_KEYS else _redact(v)
            for k, v in data.items()
        }
    if isinstance(data, list):
        return [_redact(item) for item in data]
    return data


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    vehicles_raw = {
        str(vid): _redact(vehicle.raw)
        for vid, vehicle in coordinator.data.items()
    }

    return {
        "config_entry": {
            "title": entry.title,
            "data": _redact(dict(entry.data)),
        },
        "vehicles": vehicles_raw,
    }

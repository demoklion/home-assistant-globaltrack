"""API client for GlobalTrack / LogisCarE Commander vehicle tracking platform."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)

GPS_DIVISOR = 3600000.0


class GlobalTrackAuthError(Exception):
    """Raised when authentication fails."""


class GlobalTrackConnectionError(Exception):
    """Raised when a connection error occurs."""


class GlobalTrackApiError(Exception):
    """Raised when an unexpected API error occurs."""


@dataclass
class VehicleData:
    """Parsed vehicle data from the GlobalTrack API."""

    id: int
    name: str
    plate: str
    vin: str
    kind: str
    latitude: float
    longitude: float
    altitude: int
    speed: int
    heading: int
    ignition: bool
    battery_voltage: float | None
    odometer: int
    address: str
    position_timestamp: str | None
    status_timestamp: str | None
    ride_timestamp: str | None
    raw: dict[str, Any]


def _parse_vehicle(data: dict[str, Any]) -> VehicleData:
    """Parse a single vehicle dict into a VehicleData instance."""
    pos = data.get("pos", [0, 0, 0, 0, 0, 0, 0, 0])

    # GPS coordinates are in milliarcseconds — convert to degrees.
    latitude = pos[0] / GPS_DIVISOR if len(pos) > 0 else 0.0
    longitude = pos[1] / GPS_DIVISOR if len(pos) > 1 else 0.0
    altitude = pos[2] if len(pos) > 2 else 0
    speed = pos[3] if len(pos) > 3 else 0
    heading = pos[7] if len(pos) > 7 else 0

    # Ignition from status bitmask.
    ignition = bool(data.get("status", 0) & 1)

    # Battery voltage from astatus.pwr1.
    battery_voltage: float | None = None
    astatus = data.get("astatus", {})
    if astatus and "pwr1" in astatus:
        try:
            battery_voltage = float(astatus["pwr1"])
        except (ValueError, TypeError):
            battery_voltage = None

    return VehicleData(
        id=data["id"],
        name=data.get("name", "Unknown Vehicle"),
        plate=data.get("plate", ""),
        vin=data.get("vin", ""),
        kind=data.get("kind", ""),
        latitude=latitude,
        longitude=longitude,
        altitude=altitude,
        speed=speed,
        heading=heading,
        ignition=ignition,
        battery_voltage=battery_voltage,
        odometer=data.get("tacho", 0),
        address=data.get("address", ""),
        position_timestamp=data.get("posstamp"),
        status_timestamp=data.get("statusstamp"),
        ride_timestamp=data.get("ridestamp"),
        raw=data,
    )


class GlobalTrackApi:
    """Client for the GlobalTrack / LogisCarE Commander API."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        base_url: str,
        username: str,
        password: str,
    ) -> None:
        """Initialize the API client."""
        self._session = session
        self._base_url = base_url.rstrip("/")
        self._username = username
        self._password = password
        self._ft_session: str | None = None

    async def authenticate(self) -> None:
        """Authenticate with the GlobalTrack portal and store the session cookie.

        Raises GlobalTrackAuthError on invalid credentials.
        Raises GlobalTrackConnectionError on network failures.
        """
        url = f"{self._base_url}/"
        payload = {
            "ft_username": self._username,
            "ft_password": self._password,
        }

        try:
            # Disable auto-redirect so we can capture the Set-Cookie header.
            async with self._session.post(
                url,
                data=payload,
                allow_redirects=False,
            ) as resp:
                # Extract ft_session from Set-Cookie header.
                ft_session: str | None = None
                for cookie in resp.cookies.values():
                    if cookie.key == "ft_session":
                        ft_session = cookie.value
                        break

                if not ft_session:
                    # Also check the raw Set-Cookie header as a fallback.
                    set_cookie = resp.headers.get("Set-Cookie", "")
                    if "ft_session=" in set_cookie:
                        for part in set_cookie.split(";"):
                            part = part.strip()
                            if part.startswith("ft_session="):
                                ft_session = part.split("=", 1)[1]
                                break

                if not ft_session:
                    raise GlobalTrackAuthError(
                        "Authentication failed: no session cookie received"
                    )

                self._ft_session = ft_session
                _LOGGER.debug("Successfully authenticated with GlobalTrack")

        except GlobalTrackAuthError:
            raise
        except aiohttp.ClientError as err:
            raise GlobalTrackConnectionError(
                f"Connection error during authentication: {err}"
            ) from err
        except Exception as err:
            raise GlobalTrackApiError(
                f"Unexpected error during authentication: {err}"
            ) from err

    async def async_get_vehicles(self) -> list[VehicleData]:
        """Fetch all vehicles from the GlobalTrack API.

        Handles session expiry by re-authenticating once and retrying.

        Raises GlobalTrackAuthError if re-authentication also fails.
        Raises GlobalTrackConnectionError on network failures.
        Raises GlobalTrackApiError on unexpected errors.
        """
        if self._ft_session is None:
            await self.authenticate()

        try:
            return await self._fetch_vehicles()
        except GlobalTrackAuthError:
            # Session expired — re-authenticate once and retry.
            _LOGGER.debug("Session expired, re-authenticating")
            await self.authenticate()
            return await self._fetch_vehicles()

    async def _fetch_vehicles(self) -> list[VehicleData]:
        """Perform the actual vehicle data fetch.

        Raises GlobalTrackAuthError if the response indicates an expired session.
        """
        url = f"{self._base_url}/kaview?xhr=2"

        try:
            async with self._session.post(
                url,
                cookies={"ft_session": self._ft_session},  # type: ignore[arg-type]
            ) as resp:
                content_type = resp.headers.get("Content-Type", "")

                # If the response is HTML, the session has expired.
                if "text/html" in content_type:
                    raise GlobalTrackAuthError("Session expired (HTML response)")

                if resp.status != 200:
                    raise GlobalTrackApiError(
                        f"Unexpected HTTP status {resp.status}"
                    )

                data = await resp.json()

        except GlobalTrackAuthError:
            raise
        except aiohttp.ContentTypeError as err:
            # Response wasn't valid JSON — likely an expired session.
            raise GlobalTrackAuthError(
                "Session expired (non-JSON response)"
            ) from err
        except aiohttp.ClientError as err:
            raise GlobalTrackConnectionError(
                f"Connection error fetching vehicles: {err}"
            ) from err
        except GlobalTrackApiError:
            raise
        except Exception as err:
            raise GlobalTrackApiError(
                f"Unexpected error fetching vehicles: {err}"
            ) from err

        # Parse the device list from the response.
        devices = data.get("devices", {})
        insert_list = devices.get("insert", [])

        vehicles: list[VehicleData] = []
        for device in insert_list:
            try:
                vehicles.append(_parse_vehicle(device))
            except (KeyError, IndexError, TypeError) as err:
                _LOGGER.warning(
                    "Skipping vehicle due to parse error: %s", err
                )

        _LOGGER.debug("Fetched %d vehicles from GlobalTrack", len(vehicles))
        return vehicles

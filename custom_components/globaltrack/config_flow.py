"""Config flow for GlobalTrack integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import GlobalTrackApi, GlobalTrackAuthError, GlobalTrackConnectionError
from .const import CONF_BASE_URL, DEFAULT_BASE_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Optional(CONF_BASE_URL, default=DEFAULT_BASE_URL): str,
    }
)

STEP_REAUTH_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PASSWORD): str,
    }
)


class GlobalTrackConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for GlobalTrack."""

    VERSION = 1

    _reauth_entry_data: dict[str, Any] | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            username: str = user_input[CONF_USERNAME]
            password: str = user_input[CONF_PASSWORD]
            base_url: str = user_input.get(CONF_BASE_URL, DEFAULT_BASE_URL)

            try:
                session = async_get_clientsession(self.hass)
                api = GlobalTrackApi(session, base_url, username, password)
                await api.authenticate()
                await api.async_get_vehicles()
            except GlobalTrackAuthError:
                errors["base"] = "invalid_auth"
            except GlobalTrackConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception during GlobalTrack setup")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(username.lower())
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=username,
                    data={
                        CONF_USERNAME: username,
                        CONF_PASSWORD: password,
                        CONF_BASE_URL: base_url,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_reauth(
        self, entry_data: dict[str, Any]
    ) -> ConfigFlowResult:
        """Handle reauth upon an API authentication error."""
        self._reauth_entry_data = dict(entry_data)
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reauth confirmation."""
        errors: dict[str, str] = {}

        if user_input is not None:
            assert self._reauth_entry_data is not None
            password: str = user_input[CONF_PASSWORD]
            username: str = self._reauth_entry_data[CONF_USERNAME]
            base_url: str = self._reauth_entry_data.get(
                CONF_BASE_URL, DEFAULT_BASE_URL
            )

            try:
                session = async_get_clientsession(self.hass)
                api = GlobalTrackApi(session, base_url, username, password)
                await api.authenticate()
                await api.async_get_vehicles()
            except GlobalTrackAuthError:
                errors["base"] = "invalid_auth"
            except GlobalTrackConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception(
                    "Unexpected exception during GlobalTrack reauth"
                )
                errors["base"] = "unknown"
            else:
                entry = self.hass.config_entries.async_get_entry(
                    self.context["entry_id"]
                )
                if entry:
                    self.hass.config_entries.async_update_entry(
                        entry,
                        data={
                            **self._reauth_entry_data,
                            CONF_PASSWORD: password,
                        },
                    )
                return self.async_abort(reason="reauth_successful")

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=STEP_REAUTH_DATA_SCHEMA,
            errors=errors,
        )

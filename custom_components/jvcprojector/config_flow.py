"""Config flow for JVC Projector integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components import dhcp
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DELAY, CONF_HOST, CONF_MAC, CONF_PORT, CONF_TIMEOUT
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.device_registry import format_mac
from jvc_projector import JVCCannotConnectError, JVCProjectorClient

from .const import DEFAULT_CONNECT_TIMEOUT, DEFAULT_DELAY_SECONDS, DEFAULT_PORT, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from USER_DATA_SCHEMA with values provided by the user.
    """

    projector = JVCProjectorClient(
        data[CONF_HOST], data[CONF_PORT], data[CONF_DELAY], data[CONF_TIMEOUT]
    )

    try:
        mac = format_mac(await projector.async_get_mac())
        model = await projector.async_get_model()
    except JVCCannotConnectError:
        raise CannotConnect("Could not connect to projector")

    return {CONF_MAC: mac, "model": model}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for JVC Projector."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> JVCProjectorOptionsFlowHandler:
        """JVC Projector options callback."""
        return JVCProjectorOptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initiated by the user."""

        errors = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(info[CONF_MAC])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info["model"], data=user_input)

        data_schema = {
            vol.Required(CONF_HOST): cv.string,
            vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
            vol.Optional(CONF_DELAY, default=DEFAULT_DELAY_SECONDS): float,
            vol.Optional(CONF_TIMEOUT, default=DEFAULT_CONNECT_TIMEOUT): int,
        }

        # if self.show_advanced_options:
        #     data_schema[vol.Optional(CONF_PORT, default=DEFAULT_PORT)] = int
        #     data_schema[vol.Optional(CONF_DELAY, default=DEFAULT_DELAY_SECONDS)] = float
        #     data_schema[vol.Optional(CONF_TIMEOUT, default=DEFAULT_CONNECT_TIMEOUT)] = int

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(data_schema),
            errors=errors or {},
        )

    async def async_step_dhcp(self, discovery_info: dhcp.DhcpServiceInfo) -> FlowResult:
        """Prepare configuration for a DHCP discovered JVC Projector device."""
        mac = format_mac(discovery_info.macaddress)
        ip = discovery_info.ip

        _LOGGER.info(f"Found device with mac {mac}")

        await self.async_set_unique_id(mac)
        self._abort_if_unique_id_configured(updates={CONF_HOST: ip})
        self._async_abort_entries_match({CONF_HOST: ip})

        return await self.async_step_user()


class JVCProjectorOptionsFlowHandler(config_entries.OptionsFlow):
    """Config flow options for JVC Projector"""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize JVC Projector options flow."""
        self.config_entry = config_entry
        self.port = config_entry.data[CONF_PORT]
        self.delay_seconds = config_entry.data[CONF_DELAY]
        self.host = config_entry.data[CONF_HOST]
        self.connect_timeout = config_entry.data[CONF_TIMEOUT]

        if self.config_entry.options:
            self.port = config_entry.options[CONF_PORT]
            self.delay_seconds = config_entry.options[CONF_DELAY]
            self.host = config_entry.options[CONF_HOST]
            self.connect_timeout = config_entry.options[CONF_TIMEOUT]

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        # coordinator = self.hass.data[DOMAIN][self.config_entry.entry_id]
        # proj = coordinator.projector
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_HOST, default=self.host): str,
                    vol.Optional(CONF_PORT, default=self.port): int,
                    vol.Optional(CONF_DELAY, default=self.delay_seconds): float,
                    vol.Optional(CONF_TIMEOUT, default=self.connect_timeout): int,
                }
            ),
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""

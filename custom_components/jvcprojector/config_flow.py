#!/usr/bin/env python3
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.const import CONF_HOST, CONF_PORT, CONF_TIMEOUT, CONF_PASSWORD, CONF_DELAY, CONF_MAC, CONF_MODEL, CONF_SCAN_INTERVAL, Platform
#from homeassistant.config_entries import ConfigEntry
#from homeassistant.data_entry_flow import FlowResult
#from homeassistant.helpers import instance_id
#import homeassistant.helpers.config_validation as cv
#from homeassistant.util.network import is_host_valid
#from homeassistant.core import callback
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import format_mac
from homeassistant import config_entries, exceptions
from homeassistant.util.network import is_host_valid

from .const import DOMAIN, CONF_MAX_RETRIES, DEFAULT_PORT, DEFAULT_DELAY_MS, DEFAULT_CONNECT_TIMEOUT, DEFAULT_MAX_RETRIES

from jvc_projector_remote import JVCProjector, Commands

#from . import  JVCProjectorCoordinator

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): str,
    vol.Optional(CONF_PORT, default=20554): int,
    vol.Optional(CONF_PASSWORD, default=""): str,
    vol.Optional(CONF_DELAY, default=600): int,
    vol.Optional(CONF_TIMEOUT, default=0.5): float,
    vol.Optional(CONF_MAX_RETRIES, default=5): int,
    vol.Optional(CONF_SCAN_INTERVAL, default=5): int,
})

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""

    projector = JVCProjector(data[CONF_HOST], data[CONF_PASSWORD], data[CONF_PORT], data[CONF_DELAY], data[CONF_TIMEOUT], data[CONF_MAX_RETRIES])

    connection_valid = projector.validate_connection()
    if not connection_valid:
        raise CannotConnect

    mac = format_mac(await hass.async_add_executor_job(projector.get_mac))
    model = await hass.async_add_executor_job(projector.get_model)

    return {CONF_MAC: mac, CONF_MODEL: model}

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for JVC projector integration"""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                try:
                    password = user_input[CONF_PASSWORD]
                except KeyError:
                    user_input[CONF_PASSWORD] = None

                if not is_host_valid(user_input[CONF_HOST]): raise InvalidHost
                info = await validate_input(self.hass, user_input)
                user_input[CONF_MAC]=info[CONF_MAC]
                user_input[CONF_MODEL]=info[CONF_MODEL]
                await self.async_set_unique_id(info[CONF_MAC])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info[CONF_MODEL], data=user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidHost:
                errors["host"] = "invalid_host"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA, errors=errors)


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect"""

class InvalidHost(exceptions.HomeAssistantError):
    """Error to indicate there is an invalid hostname"""

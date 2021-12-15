"""The JVC Projector integration."""
from __future__ import annotations

import asyncio
from collections.abc import Iterable
from datetime import timedelta
import logging
from typing import Final

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DELAY, CONF_HOST, CONF_PORT, CONF_TIMEOUT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from jvc_projector import JVCCommandNotFoundError, JVCProjectorClient
from jvc_projector.jvcprojector import JVCPoweredOffError

from .const import ATTR_INPUT, ATTR_SIGNAL, DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: Final[list[Platform]] = [Platform.REMOTE]
SCAN_INTERVAL: Final = timedelta(seconds=10)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up JVC Projector from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    delay = entry.data[CONF_DELAY]
    timeout = entry.data[CONF_TIMEOUT]

    if entry.options:
        host = entry.options[CONF_HOST]
        port = entry.options[CONF_PORT]
        delay = entry.options[CONF_DELAY]
        timeout = entry.options[CONF_TIMEOUT]

    coordinator = JVCProjectorCoordinator(hass, host, port, delay, timeout)
    entry.async_on_unload(entry.add_update_listener(update_listener))
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = coordinator

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


class JVCProjectorCoordinator(DataUpdateCoordinator[None]):
    """Representation of a JVC Projector Coordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        port: int = None,
        delay_seconds: float = None,
        connect_timeout_seconds: int = None,
    ) -> None:
        """Initialize JVC Projector Client."""

        self.power_state: str | None = None
        self.is_on: bool = False
        self.signal: str | None = None
        self.input: str | None = None
        self.last_command_sent: str | None = None
        self.state_lock = asyncio.Lock()
        self.attrs = {}
        self.projector = JVCProjectorClient(
            host, port, delay_seconds, connect_timeout_seconds
        )

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )

    async def async_update_projector_params(
        self, new_host, new_port, new_delay_seconds, new_connect_timeout
    ) -> None:
        async with self.state_lock:
            self.projector = JVCProjectorClient(
                new_host,
                port=new_port,
                delay_seconds=new_delay_seconds,
                connect_timeout_seconds=new_connect_timeout,
            )

    async def _async_update_data(self) -> None:
        async with self.state_lock:
            self.is_on: bool = await self.projector.async_is_on()
            self.power_state: str | None = await self.projector.async_get_power_state()
            # self.input: str | None = None
            try:
                input_signal = await self.projector.async_get_input()
                self.input = input_signal["input"]
                self.signal = input_signal["signal"]
            except JVCPoweredOffError:
                _LOGGER.info("Can't fetch input state, the projector is powered off.")
                self.input = "N/A"
                self.signal = "N/A"

            self.attrs[ATTR_INPUT] = self.input
            self.attrs[ATTR_SIGNAL] = self.signal

    async def async_send_command(self, commands: Iterable[str]) -> None:
        """Send commands to projector."""
        async with self.state_lock:
            for command in commands:
                try:
                    await self.projector.async_command(command)
                    self.last_command_sent = command
                    await self.async_request_refresh()
                except JVCCommandNotFoundError:
                    _LOGGER.error("No command with name %s found." % (command))
                except JVCPoweredOffError:
                    _LOGGER.error(
                        "Cannot send command. The projector is not powered on."
                    )

    async def async_turn_on(self) -> None:
        """Turn on the projector."""
        async with self.state_lock:
            await self.projector.async_power_on()
            await self.async_request_refresh()

    async def async_turn_off(self) -> None:
        """Turn off the projector."""
        async with self.state_lock:
            await self.projector.async_power_off()
            await self.async_request_refresh()

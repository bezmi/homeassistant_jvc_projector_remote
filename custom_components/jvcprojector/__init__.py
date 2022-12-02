"""Support for JVC Projector devices."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from homeassistant.const import CONF_HOST, CONF_PORT, CONF_TIMEOUT, CONF_PASSWORD, CONF_DELAY, Platform

from jvc_projector_remote import JVCProjector

from .const import DOMAIN, CONF_MAX_RETRIES
from .coordinator import JVCProjectorCoordinator

from typing import Final

PLATFORMS: Final[list[Platform]] = [
    Platform.REMOTE,
]

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up JVC Projector from config entry"""
    host = config_entry.data[CONF_HOST]
    port = config_entry.data[CONF_PORT]
    password = config_entry.data[CONF_PASSWORD]
    delay = config_entry.data[CONF_DELAY]
    timeout = config_entry.data[CONF_TIMEOUT]
    max_retries = config_entry.data[CONF_MAX_RETRIES]

    client = JVCProjector(host, password, port, delay, timeout, max_retries)

    coordinator = JVCProjectorCoordinator(hass=hass, client=client, config=config_entry.data)

    config_entry.async_on_unload(config_entry.add_update_listener(update_listener))

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = coordinator

    # hass.config_entries.async_setup_platforms(config_entry, PLATFORMS)

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok

async def update_listener(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Handle optiosn update"""
    await hass.config_entries.async_reload(config_entry.entry_id)

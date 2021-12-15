"""JVC Projector remote platform"""
from __future__ import annotations
import logging

from collections.abc import Iterable
from typing import Any

from homeassistant.components.remote import RemoteEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import DOMAIN, HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_DELAY, CONF_TIMEOUT

from .const import DEFAULT_NAME, ATTR_MANUFACTURER, DOMAIN

from . import JVCProjectorCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback
) -> None:
    """Set up JVC projector Remote from a config entry."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    # host = config_entry.options.get(CONF_HOST)
    # port = config_entry.options.get(CONF_PORT)
    # delay = config_entry.options.get(CONF_DELAY)
    # timeout = config_entry.options.get(CONF_TIMEOUT)
    # await coordinator.async_update_projector_params(host, port, delay, timeout)
    unique_id = config_entry.unique_id
    assert unique_id is not None
    device_info = DeviceInfo(
        identifiers={(DOMAIN, unique_id)},
        manufacturer=ATTR_MANUFACTURER,
        model=config_entry.title,
        name=DEFAULT_NAME,
    )
    # config_entry.async_on_unload(config_entry.add_update_listener(update_listener))

    async_add_entities([JVCProjectorRemote(coordinator, DEFAULT_NAME, unique_id, device_info)])

# async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
#     """Handle options update."""
#     host = entry.options[CONF_HOST]
#     port = entry.options[CONF_PORT]
#     delay = entry.options[CONF_DELAY]
#     timeout = entry.options[CONF_TIMEOUT]
#     _LOGGER.error("update_listener remote")
#     _LOGGER.error("%s %d %f %d" % (host, port, delay, timeout))
#     print("remote update", entry.entry_id)
#     coordinator = JVCProjectorCoordinator(hass, host, port, delay, timeout)
#     # await coordinator.async_config_entry_first_refresh()
#     hass.data[DOMAIN][entry.entry_id] = coordinator
#     print(hass.data[DOMAIN][entry.entry_id].projector._delay_seconds)
#     # await hass.data[DOMAIN][entry.entry_id].async_config_entry_first_refresh()
#     # await coordinator.async_update_projector_params(host, port, delay, timeout)
#     await hass.config_entries.async_reload(entry.entry_id)


class JVCProjectorRemote(CoordinatorEntity, RemoteEntity):
    """Representation of a JVC Projector Remote"""
    coordinator: JVCProjectorCoordinator

    def __init__(
            self,
            coordinator: JVCProjectorCoordinator,
            name: str,
            unique_id: str,
            device_info: DeviceInfo,
    ) -> None:
        """Initialize the entity."""

        self._attr_device_info = device_info
        self._attr_name = name
        self._attr_unique_id = unique_id

        super().__init__(coordinator)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra attributes"""
        return self.coordinator.attrs

    @property
    def is_on(self) -> bool:
        """Return true if device is on."""
        return self.coordinator.is_on

    @property
    def signal(self) -> str | None:
        """Return the current signal status"""
        return self.coordinator.signal

    @property
    def power_state(self) -> str | None:
        """Return the current power state"""
        return self.coordinator.power_state

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the device on."""
        self.coordinator.is_on = True
        await self.coordinator.async_turn_on()
        # self.schedule_update_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the device off."""
        self.coordinator.is_on = False
        await self.coordinator.async_turn_off()
        # self.schedule_update_ha_state()

    async def async_send_command(self, command: Iterable[str], **kwargs: Any) -> None:
        """Send a command to the device."""
        await self.coordinator.async_send_command(command)
            # self.schedule_update_ha_state()

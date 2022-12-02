import logging
from homeassistant.components.remote import RemoteEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN, DEFAULT_NAME
from .entity import JVCProjectorEntity
from .coordinator import JVCProjectorCoordinator

from homeassistant.const import (
    CONF_MAC,
    CONF_MODEL,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up the remote."""
    coordinator: JVCProjectorCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    unique_id = f"{config_entry.data[CONF_MAC]}_remote"
    assert unique_id is not None
    async_add_entities(
        [
            JVCProjectorRemote(coordinator, unique_id, config_entry.data[CONF_MODEL], DEFAULT_NAME)
        ],
        True,
    )

class JVCProjectorRemote(JVCProjectorEntity, RemoteEntity):
    """Home assistant JVC remote representation"""

    @property
    def extra_state_attributes(self) -> dict:
        """Return device state attributes."""

        return {
            "last_commands_sent": self.coordinator.last_commands_sent,
            "last_commands_response": self.coordinator.last_commands_response,
            "power_state": self.coordinator.power_state,
            "signal_state": self.coordinator.signal_state,
            "input_state": self.coordinator.input_state,
            "lamp_state": self.coordinator.lamp_state,
            "picture_mode": self.coordinator.picture_mode_state,
        }

    @property
    def is_on(self) -> bool:
        return self.coordinator.is_on

    async def async_turn_on(self) -> None:
        """Turn the remote on."""
        if self.is_on:
            return
        self._attr_is_on = True
        self.coordinator.is_on = True
        await self.coordinator.async_turn_on()
        self.async_write_ha_state()
        # await self.coordinator.async_request_refresh()

    async def async_turn_off(self) -> None:
        """Turn the remote off."""
        if not self.is_on:
            return
        self._attr_is_on = False
        self.coordinator.is_on = False
        await self.coordinator.async_turn_off()
        self.async_write_ha_state()

    async def async_send_command(self, command, delay_secs=0, **kwargs) -> None:
        """Send a command to a device."""
        await self.coordinator.async_send_command(command, delay_secs)

import logging
from homeassistant.components import remote
from homeassistant.const import DEVICE_DEFAULT_NAME
from homeassistant import util
import asyncio

from homeassistant.const import (CONF_HOST, CONF_NAME, CONF_PASSWORD)
_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the remote."""
    if config.get(CONF_HOST) is not None:
        host = config.get(CONF_HOST)
        name = config.get(CONF_NAME)
        password = config.get(CONF_PASSWORD)
    add_entities([
        JVCRemote(name, host, password),
    ])


class JVCRemote(remote.RemoteEntity):
    """Home assistant JVC remote representation"""

    def __init__(self, name, host, password):
        """Initialize the Remote."""
        from jvc_projector import JVCProjector
        self._name = name or DEVICE_DEFAULT_NAME
        self._host = host
        self._password = password
        self._last_command_sent = None
        self._jvc = JVCProjector(host, password)
        self._state = None
        self._power_state = 'N/A'
        self.state_lock = asyncio.Lock()

    @property
    def should_poll(self):
        # poll the device so we know if it was state changed
        # via an external method, like the physical remote
        return True

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    async def async_update(self):
        await self.async_update_state()

    @property
    def is_on(self):
        """Return true if remote is on."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return device state attributes."""

        if self._power_state in ['lamp_on', 'reserved']:
            self._state = True
        else:
            self._state = False

        return {
            'last_command_sent': self._last_command_sent if self._last_command_sent is not None else 'N/A',
            'power_state': self._power_state,
        }

    async def async_turn_on(self, **kwargs):
        """Turn the remote on."""
        await self.async_send_command('power_on')
        self._state = True

    async def async_turn_off(self, **kwargs):
        """Turn the remote off."""
        await self.async_send_command('power_off')
        self._state = False

    async def async_send_command(self, command, **kwargs):
        """Send a command to a device."""

        async with self.state_lock:
            if type(command) != list:
                command = [command]

            for com in command:
                _LOGGER.info(f"sending command: {com}")
                try:
                    command_sent = await hass.async_add_executor_job(self._jvc.command(com))
                except Exception:
                    # when an error occured during sending, command execution probably failed
                    command_sent = False

                if not command_sent:
                    self._last_command_sent = "N/A"
                    continue
                else:
                    self._last_command_sent = com

    async def async_update_state(self):
        """"Update the state with the Power Status (if available)"""

        # do nothing until lock is released
        if self.state_lock.locked():
            return

        try:
            self._power_state = await hass.async_add_executor_job(self._jvc.power_state())
        except Exception:
            self._power_state = 'unknown'

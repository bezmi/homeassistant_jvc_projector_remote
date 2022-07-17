import logging
from homeassistant.components import remote
from homeassistant.const import DEVICE_DEFAULT_NAME
from homeassistant import util
import asyncio
from typing import Final
from jvc_projector import JVCCommunicationError as comm_error
import datetime

JVC_RETRIES: Final = "max_retries"

from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_TIMEOUT,
    CONF_DELAY,
)

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_entities, discovery_info=None) -> None:
    """Set up the remote."""
    if config.get(CONF_HOST) is not None:
        host = config.get(CONF_HOST)
        port = config.get(CONF_PORT)
        name = config.get(CONF_NAME)
        password = config.get(CONF_PASSWORD)
        timeout = config.get(CONF_TIMEOUT)
        delay = config.get(CONF_DELAY)
        retries = config.get(JVC_RETRIES)
    add_entities(
        [
            JVCRemote(name, host, password, port, delay, timeout, retries),
        ]
    )


class JVCRemote(remote.RemoteEntity):
    """Home assistant JVC remote representation"""

    def __init__(
        self,
        name: str | None,
        host: str,
        password: str | None,
        port: int | None,
        delay: int | None,
        timeout: float | None,
        retries: int | None,
    ) -> None:
        """Initialize the Remote."""
        from jvc_projector import JVCProjector

        self._name = name or DEVICE_DEFAULT_NAME
        self._host = host
        self._password = password

        self._last_commands_sent = None
        self._jvc = JVCProjector(host, password, port, delay, timeout, retries)
        self._power_state = self._jvc.power_state()
        self._state = True if self._power_state == "lamp_on" else False
        self._signal_state = (
            "unknown" if not self._state else self._jvc.command("signal")
        )
        self._input_state = "unknown" if not self._state else self._jvc.command("input")
        self._lamp_state = "unknown" if not self._state else self._jvc.command("lamp")
        self._picture_mode_state = (
            "unknown" if not self._state else self._jvc.command("picture_mode")
        )
        self._last_commands_response = None
        self.state_lock = asyncio.Lock()

    @property
    def should_poll(self) -> bool:
        # poll the device so we know if it was state changed
        # via an external method, like the physical remote
        return True

    @property
    def name(self) -> str:
        """Return the name of the device if any."""
        return self._name

    async def async_update(self):
        await self.async_update_state()

    @property
    def is_on(self) -> bool:
        """Return true if remote is on."""
        return self._state

    @property
    def extra_state_attributes(self) -> dict:
        """Return device state attributes."""

        if self._power_state in ["lamp_on", "reserved"]:
            self._state = True
        else:
            self._state = False

        return {
            "last_commands_sent": self._last_commands_sent,
            "last_commands_response": self._last_commands_response,
            "power_state": self._power_state,
            "signal_state": self._signal_state,
            "input_state": self._input_state,
            "lamp_state": self._lamp_state,
            "picture_mode": self._picture_mode_state,
        }

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the remote on."""
        if self._state:
            return
        await self.async_send_command("power-on")
        self._state = True

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the remote off."""
        if not self._state:
            return
        await self.async_send_command("power-off")
        self._state = False

    async def async_send_command(self, command, delay_secs=0, **kwargs) -> None:
        """Send a command to a device."""

        async with self.state_lock:
            if type(command) != list:
                command = [command]

            self._last_commands_sent = []
            self._last_commands_response = []

            for com in command:
                _LOGGER.info(f"sending command: {com}")
                try:
                    resp = await self.hass.async_add_executor_job(
                        self._jvc.command, (com)
                    )
                    if resp is None:
                        resp = "success"
                    self._last_commands_sent.append(com)
                    self._last_commands_response.append(resp)
                except comm_error as e:
                    # The projector is powered off
                    _LOGGER.warning(
                        f"Failed to send command, could not communicate with projector: {repr(e)}\nThis could happen if the command only works when the projector is on but the current state is off, or the timeout setting is too low"
                    )
                    self._last_commands_sent.append(com)
                    self._last_commands_response.append("failed")
                except Exception as e:
                    # when an error occured during sending, command execution probably failed
                    _LOGGER.error(f"Unknown error, abort sending commands")
                    self._last_commands_sent = ["unknown"]
                    self._last_commands_response = ["failed"]
                    raise e

                self.async_write_ha_state()
                delta = (
                    datetime.datetime.now() - self._jvc.last_command_time
                ).total_seconds()
                if delay_secs >= delta:
                    _LOGGER.debug(f"waiting {delay_secs} seconds before next command")
                    await asyncio.sleep(delay_secs - delta)

    async def async_update_state(self) -> None:
        """ "Update the state with the Power Status (if available)"""

        # do nothing until lock is released
        if self.state_lock.locked():
            return

        try:
            self._power_state = await self.hass.async_add_executor_job(
                self._jvc.power_state
            )

            if self._power_state != "lamp_on":
                (
                    self._input_state,
                    self._signal_state,
                    self._picture_mode_state,
                    self._lamp_state,
                ) = ("unknown", "unknown", "unknown", "unknown")
                return

            self._input_state = await self.hass.async_add_executor_job(
                self._jvc.command, ("input")
            )
            self._signal_state = await self.hass.async_add_executor_job(
                self._jvc.command, ("signal")
            )
            self._picture_mode_state = await self.hass.async_add_executor_job(
                self._jvc.command, ("picture_mode")
            )
            self._lamp_state = await self.hass.async_add_executor_job(
                self._jvc.command, ("lamp")
            )

        except Exception as e:
            self._power_state = "unknown"
            raise e

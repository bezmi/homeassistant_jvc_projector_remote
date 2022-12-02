#!/usr/bin/env python3
"""Update coordinator for JVC projector integration"""
from __future__ import annotations


import logging

from homeassistant.components import remote
from homeassistant.const import DEVICE_DEFAULT_NAME
from homeassistant import util
import asyncio
from types import MappingProxyType
from typing import Any, Final
from jvc_projector_remote import JVCCommunicationError as comm_error
from jvc_projector_remote import JVCConfigError as conf_error
from jvc_projector_remote import JVCCannotConnectError as connect_error
from jvc_projector_remote import JVCPoweredOffError as power_error
from jvc_projector_remote import JVCProjector
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import datetime
from .const import DOMAIN
from .const import DEFAULT_NAME, CONF_MAX_RETRIES

from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_TIMEOUT,
    CONF_DELAY,
    CONF_MAC,
)

_LOGGER = logging.getLogger(__name__)

class JVCProjectorCoordinator(DataUpdateCoordinator[None]):
    """Representation of a JVC projector Coordinator"""

    def __init__(
            self,
            hass: HomeAssistant,
            client: JVCProjector,
            config: MappingProxyType[str, Any],
    ) -> None:

        self.client: JVCProjector = client
        self.conf_mac: str = config[CONF_MAC]
        self.conf_delay: int = config[CONF_DELAY]
        self.conf_host: str = config[CONF_HOST]
        self.conf_port: int = config[CONF_PORT]
        self.conf_timeout: float = config[CONF_TIMEOUT]
        self.conf_max_retries: int = config[CONF_MAX_RETRIES]

        self.input_state: str | None = None
        self.signal_state: str | None = None
        self.picture_mode_state: str | None = None
        self.lamp_state: str | None = None
        # self.available: bool = True
        self.is_on: bool = False
        self.state_lock = asyncio.Lock()
        self.last_commands_sent = []
        self.last_commands_response = []


        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=datetime.timedelta(seconds=config[CONF_SCAN_INTERVAL]),
            request_refresh_debouncer=Debouncer(
                hass, _LOGGER, cooldown=1.0, immediate=False
            ),
        )

    async def async_turn_on(self) -> None:
        """Turn the projector on."""
        await self.async_send_command("power-on")

    async def async_turn_off(self) -> None:
        """Turn the projector on."""
        await self.async_send_command("power-off")

    async def async_send_command(self, command, delay_secs=0) -> None:
        """Send a command to a device."""

        async with self.state_lock:

            if self.power_state == "not_connected":
                _LOGGER.warning(f"The projector is not connected, cannot send command")
                (
                    self.input_state,
                    self.signal_state,
                    self.picture_mode_state,
                    self.lamp_state,
                ) = ("unknown", "unknown", "unknown", "unknown")
                self.last_commands_sent = []
                self.last_commands_response = []
                return

            if type(command) != list:
                command = [command]

            self.last_commands_sent = []
            self.last_commands_response = []

            for com in command:
                _LOGGER.info(f"sending command: {com}")
                try:
                    resp = await self.hass.async_add_executor_job(
                        self.client.command, (com)
                    )
                    if resp is None:
                        resp = "success"
                    self.last_commands_sent.append(com)
                    self.last_commands_response.append(resp)
                except comm_error as e:
                    # The projector is powered off
                    _LOGGER.warning(
                        f"Sent command, received communication error: {repr(e)}"
                    )
                    self.last_commands_sent.append(com)
                    self.last_commands_response.append("failed")
                except power_error as e:
                    _LOGGER.warning(f"Sent command, received power error: {repr(e)}")
                    self.last_commands_sent.append(com)
                    self.last_commands_response.append("failed")
                except connect_error as e:
                    # the projector is likely off at the mains
                    _LOGGER.warning(f"The projector at {self.conf_host}:{self.conf_port} did not respond to the connection request: {repr(e)}")
                    self.power_state = "not_connected"
                    self.last_commands_sent = ["unknown"]
                    self.last_commands_response = ["failed"]
                    return

                except Exception as e:
                    # when an error occured during sending, command execution probably failed
                    _LOGGER.error(f"Unhandled error, abort sending commands")
                    self.last_commands_sent = ["unknown"]
                    self.last_commands_response = ["failed"]
                    raise e

                # self.async_write_ha_state()

                delta = (
                    datetime.datetime.now() - self.client.last_command_time
                ).total_seconds()
                if delay_secs >= delta:
                    _LOGGER.debug(f"waiting {delay_secs} seconds before next command")
                    await asyncio.sleep(delay_secs - delta)

    async def _async_update_data(self) -> None:
        """ "Update the state with the Power Status (if available)"""
        _LOGGER.warning("updating data")

        # do nothing until lock is released
        if self.state_lock.locked():
            return

        # in case the init of the JVCProjector object failed due to a JVCConfigError
        # is_connected = await self.hass.async_add_executor_job(self.client.validate_connection)
        # if not is_connected:
        #     _LOGGER.warning(f"Couldn't connect to the projector at the specified address: {self.conf_host}:{self.conf_port}. Ensure the configuration is correct.")
        #     self.power_state = "not_connected"
        #     # self.available = False
        #     self.is_on = False
        #     (
        #         self.input_state,
        #         self.signal_state,
        #         self.picture_mode_state,
        #         self.lamp_state,
        #     ) = ("unknown", "unknown", "unknown", "unknown")
        #     return

        # self.available = True
        try:
            self.power_state = await self.hass.async_add_executor_job(
                self.client.power_state
            )
            if self.power_state in ["lamp_on", "reserved"]:
                self.is_on = True
            else:
                self.is_on = False

            if self.power_state != "lamp_on":
                (
                    self.input_state,
                    self.signal_state,
                    self.picture_mode_state,
                    self.lamp_state,
                ) = ("unknown", "unknown", "unknown", "unknown")
                return

            self.input_state = await self.hass.async_add_executor_job(
                self.client.command, ("input")
            )
            self.signal_state = await self.hass.async_add_executor_job(
                self.client.command, ("signal")
            )

            # on some models (tested on X5900 and X30). The 'picture_mode' command times out if
            # there is no active signal going to the HDMI output.
            if self.signal_state in ('no_signal' or 'unknown'):
                self.picture_mode_state = 'unknown'
                _LOGGER.info(
                    f"Skip fetching picture_mode state as signal state is 'unknown' or 'no_signal'."
                )
            else:
                self.picture_mode_state = await self.hass.async_add_executor_job(
                    self.client.command, ("picture_mode")
                )

            self.lamp_state = await self.hass.async_add_executor_job(
                self.client.command, ("lamp")
            )

        except connect_error as e:
            _LOGGER.warning(f"The projector at {self.conf_host}:{self.conf_port} did not respond to the connection request.")
            #self.available = False
            self.power_state = "not_connected"
            (
                self.input_state,
                self.signal_state,
                self.picture_mode_state,
                self.lamp_state,
            ) = ("unknown", "unknown", "unknown", "unknown")
            return
        except comm_error as e:
            _LOGGER.warning(
                f"Failed to update state, received communication error : {repr(e)}."
            )
            self.power_state = "unknown"
            (
                self.input_state,
                self.signal_state,
                self.picture_mode_state,
                self.lamp_state,
            ) = ("unknown", "unknown", "unknown", "unknown")
            return

        except Exception as e:
            _LOGGER.error(f"Unhandled error occured")
            self.power_state = "unknown"
            raise e

#!/usr/bin/env python3
"""Constants for the JVC Projector integration."""
from __future__ import annotations

from typing import Final

DOMAIN: Final = "jvcprojector"
ATTR_MANUFACTURER: Final = "JVC"

CONF_MAX_RETRIES: Final = "max_retries"
CONF_NETWORK_PASSWORD: Final = "network_password"

DEFAULT_PORT: Final = 20554
DEFAULT_DELAY_MS: Final = 700
DEFAULT_CONNECT_TIMEOUT: Final = 0.5
DEFAULT_MAX_RETRIES: Final = 5
DEFAULT_NAME: Final = "JVC Projector"

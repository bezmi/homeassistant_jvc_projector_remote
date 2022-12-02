#!/usr/bin/env python3
"""Constants for the JVC Projector integration."""
from __future__ import annotations

from typing import Final

DOMAIN: Final = "jvcprojector"
ATTR_MANUFACTURER: Final = "JVC Kenwood"

CONF_MAX_RETRIES: Final = "max_retries"

DEFAULT_PORT: Final = 20554
DEFAULT_DELAY_MS: Final = 600
DEFAULT_CONNECT_TIMEOUT: Final = 0.5
DEFAULT_MAX_RETRIES: Final = 5
DEFAULT_NAME: Final = "JVC Projector"

ATTR_INPUT: Final = "input"
ATTR_SIGNAL: Final = "signal"

#!/usr/bin/env python3
"""An entity class for JVC projector integration"""

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import JVCProjectorCoordinator
from .const import ATTR_MANUFACTURER, DOMAIN

class JVCProjectorEntity(CoordinatorEntity[JVCProjectorCoordinator]):
    """JVC projector entity class."""
    _attr_has_entity_name = True

    def __init__(
            self,
            coordinator: JVCProjectorCoordinator,
            unique_id: str,
            model: str,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)

        self._attr_unique_id = unique_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, unique_id)},
            manufacturer=ATTR_MANUFACTURER,
            model=model,
            name=f"{ATTR_MANUFACTURER} {model}",
        )

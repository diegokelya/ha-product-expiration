"""Sensor platform for Product Expiration Tracker."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ProductExpirationCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Product Expiration sensors."""
    coordinator: ProductExpirationCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    sensors = [
        ProductCountSensor(coordinator, entry),
        ExpiredCountSensor(coordinator, entry),
        ExpiringSoonCountSensor(coordinator, entry),
        NextExpirySensor(coordinator, entry),
    ]

    async_add_entities(sensors)


class ProductExpirationSensorBase(CoordinatorEntity, SensorEntity):
    """Base class for Product Expiration sensors."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ProductExpirationCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Product Expiration Tracker",
            "manufacturer": "Custom",
            "model": "Product Tracker",
        }


class ProductCountSensor(ProductExpirationSensorBase):
    """Sensor for total product count."""

    _attr_name = "Total Products"
    _attr_icon = "mdi:food-apple"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: ProductExpirationCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_total_products"
        self._entry_id = entry.entry_id

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return self.coordinator.data.get("total_count", 0)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        products = self.coordinator.data.get("products", [])
        photo_base_url = self.coordinator.data.get("photo_base_url")
        
        return {
            "products": [
                {
                    "id": p.get("id"),
                    "name": p.get("name"),
                    "expiry": p.get("expiry"),
                    "days_until_expiry": p.get("days_until_expiry"),
                    "status": p.get("status", {}).get("label"),
                    "quantity": p.get("quantity", 1),
                    "category": p.get("category"),
                    "location": p.get("location"),
                    "image": p.get("image"),
                    "image_url": p.get("image_url"),
                }
                for p in products[:100]  # Limit to prevent state too large
            ],
            "photo_base_url": photo_base_url,
            "warn_days": self.coordinator.data.get("warn_days"),
        }


class ExpiredCountSensor(ProductExpirationSensorBase):
    """Sensor for expired product count."""

    _attr_name = "Expired Products"
    _attr_icon = "mdi:alert-circle"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: ProductExpirationCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_expired_products"

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return self.coordinator.data.get("expired_count", 0)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        expired = self.coordinator.data.get("expired", [])
        return {
            "products": [
                {
                    "id": p.get("id"),
                    "name": p.get("name"),
                    "expiry": p.get("expiry"),
                    "days_since_expiry": abs(p.get("days_until_expiry", 0)),
                }
                for p in expired
            ]
        }


class ExpiringSoonCountSensor(ProductExpirationSensorBase):
    """Sensor for products expiring soon."""

    _attr_name = "Expiring Soon"
    _attr_icon = "mdi:alert-circle-outline"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: ProductExpirationCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_expiring_soon"

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return self.coordinator.data.get("expiring_soon_count", 0)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        expiring = self.coordinator.data.get("expiring_soon", [])
        return {
            "products": [
                {
                    "id": p.get("id"),
                    "name": p.get("name"),
                    "expiry": p.get("expiry"),
                    "days_until_expiry": p.get("days_until_expiry"),
                }
                for p in expiring
            ]
        }


class NextExpirySensor(ProductExpirationSensorBase):
    """Sensor for next product to expire."""

    _attr_name = "Next Expiry"
    _attr_icon = "mdi:calendar-alert"

    def __init__(
        self,
        coordinator: ProductExpirationCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_next_expiry"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        next_product = self.coordinator.data.get("next_product")
        if next_product:
            return next_product.get("name")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        next_product = self.coordinator.data.get("next_product")
        if next_product:
            return {
                "id": next_product.get("id"),
                "expiry_date": next_product.get("expiry"),
                "days_until_expiry": next_product.get("days_until_expiry"),
                "status": next_product.get("status", {}).get("label"),
                "quantity": next_product.get("quantity", 1),
            }
        return {}

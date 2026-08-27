"""Product Expiration Tracker for Home Assistant."""
from __future__ import annotations

import logging
from datetime import date, datetime

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

from .const import DOMAIN
from .coordinator import ProductExpirationCoordinator
from .storage import ProductStorage

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

# Service schemas
SERVICE_ADD_PRODUCT_SCHEMA = vol.Schema({
    vol.Required("name"): cv.string,
    vol.Required("expiry"): cv.date,
    vol.Optional("image"): cv.string,
    vol.Optional("literal_text"): cv.string,
    vol.Optional("confidence"): vol.In(["alta", "media", "baja", "confirmada por usuario"]),
    vol.Optional("barcode"): cv.string,
    vol.Optional("quantity", default=1): cv.positive_int,
    vol.Optional("category"): cv.string,
    vol.Optional("location"): cv.string,
})

SERVICE_REMOVE_PRODUCT_SCHEMA = vol.Schema({
    vol.Required("product_id"): cv.string,
})

SERVICE_UPDATE_PRODUCT_SCHEMA = vol.Schema({
    vol.Required("product_id"): cv.string,
    vol.Optional("name"): cv.string,
    vol.Optional("expiry"): cv.date,
    vol.Optional("quantity"): cv.positive_int,
    vol.Optional("image"): cv.string,
    vol.Optional("category"): cv.string,
    vol.Optional("location"): cv.string,
})

SERVICE_IMPORT_PRODUCTS_SCHEMA = vol.Schema({
    vol.Required("products"): vol.All(cv.ensure_list, [dict]),
})


def _normalize_date(value: date | datetime | str) -> str:
    """Normalize date to ISO string."""
    if isinstance(value, datetime):
        return value.date().isoformat()
    elif isinstance(value, date):
        return value.isoformat()
    elif isinstance(value, str):
        return value
    else:
        raise ValueError(f"Invalid date type: {type(value)}")


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Product Expiration component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Product Expiration from a config entry."""
    # Only allow one instance
    if len(hass.config_entries.async_entries(DOMAIN)) > 1:
        _LOGGER.warning("Only one Product Expiration instance is allowed")
    
    storage = ProductStorage(hass)
    await storage.async_load()
    
    coordinator = ProductExpirationCoordinator(hass, storage, entry)
    await coordinator.async_config_entry_first_refresh()
    
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "storage": storage,
    }
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Register services only once
    if not hass.services.has_service(DOMAIN, "add_product"):
        async def add_product(call: ServiceCall) -> None:
            """Add a new product."""
            product_data = dict(call.data)
            # Normalize date
            if "expiry" in product_data:
                try:
                    product_data["expiry"] = _normalize_date(product_data["expiry"])
                except ValueError as err:
                    raise HomeAssistantError(f"Invalid expiry date: {err}") from err
            
            await storage.async_add_product(product_data)
            await coordinator.async_refresh()
        
        async def remove_product(call: ServiceCall) -> None:
            """Remove a product."""
            product_id = call.data["product_id"]
            removed = await storage.async_remove_product(product_id)
            if not removed:
                raise HomeAssistantError(f"Product not found: {product_id}")
            await coordinator.async_refresh()
        
        async def update_product(call: ServiceCall) -> None:
            """Update a product."""
            product_id = call.data["product_id"]
            updates = {k: v for k, v in call.data.items() if k != "product_id"}
            
            # Normalize date if present
            if "expiry" in updates:
                try:
                    updates["expiry"] = _normalize_date(updates["expiry"])
                except ValueError as err:
                    raise HomeAssistantError(f"Invalid expiry date: {err}") from err
            
            updated = await storage.async_update_product(product_id, updates)
            if not updated:
                raise HomeAssistantError(f"Product not found: {product_id}")
            await coordinator.async_refresh()
        
        async def import_products(call: ServiceCall) -> None:
            """Import multiple products."""
            products = call.data["products"]
            imported = 0
            errors = []
            
            for idx, product in enumerate(products):
                try:
                    if "expiry" in product:
                        product["expiry"] = _normalize_date(product["expiry"])
                    await storage.async_add_product(product)
                    imported += 1
                except Exception as err:
                    errors.append(f"Product {idx}: {err}")
            
            await coordinator.async_refresh()
            
            if errors:
                raise HomeAssistantError(
                    f"Imported {imported}/{len(products)} products. Errors: {'; '.join(errors)}"
                )
        
        hass.services.async_register(
            DOMAIN, "add_product", add_product, schema=SERVICE_ADD_PRODUCT_SCHEMA
        )
        hass.services.async_register(
            DOMAIN, "remove_product", remove_product, schema=SERVICE_REMOVE_PRODUCT_SCHEMA
        )
        hass.services.async_register(
            DOMAIN, "update_product", update_product, schema=SERVICE_UPDATE_PRODUCT_SCHEMA
        )
        hass.services.async_register(
            DOMAIN, "import_products", import_products, schema=SERVICE_IMPORT_PRODUCTS_SCHEMA
        )
    
    # Listen for options updates
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    
    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        
        # Unregister services only if this was the last entry
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, "add_product")
            hass.services.async_remove(DOMAIN, "remove_product")
            hass.services.async_remove(DOMAIN, "update_product")
            hass.services.async_remove(DOMAIN, "import_products")
    
    return unload_ok

"""Storage handler for Product Expiration."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import STORAGE_KEY, STORAGE_VERSION

_LOGGER = logging.getLogger(__name__)


class ProductStorage:
    """Manage product storage."""
    
    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the storage."""
        self.hass = hass
        self._store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._data: dict[str, Any] = {"products": []}
    
    async def async_load(self) -> None:
        """Load data from storage."""
        data = await self._store.async_load()
        if data is not None:
            self._data = data
        else:
            self._data = {"products": []}
    
    async def async_save(self) -> None:
        """Save data to storage."""
        await self._store.async_save(self._data)
    
    async def async_add_product(self, product: dict[str, Any]) -> str:
        """Add a new product."""
        # Generate unique ID using UUID
        product_id = product.get("id") or str(uuid.uuid4())
        product["id"] = product_id
        product["added_at"] = datetime.now().isoformat()
        
        self._data["products"].append(product)
        await self.async_save()
        return product_id
    
    async def async_remove_product(self, product_id: str) -> bool:
        """Remove a product."""
        original_count = len(self._data["products"])
        self._data["products"] = [
            p for p in self._data["products"] if p.get("id") != product_id
        ]
        
        if len(self._data["products"]) < original_count:
            await self.async_save()
            return True
        return False
    
    async def async_update_product(self, product_id: str, updates: dict[str, Any]) -> bool:
        """Update a product."""
        for product in self._data["products"]:
            if product.get("id") == product_id:
                product.update(updates)
                await self.async_save()
                return True
        return False
    
    def get_products(self) -> list[dict[str, Any]]:
        """Get all products."""
        return self._data.get("products", [])
    
    async def async_import_products(self, products: list[dict[str, Any]]) -> int:
        """Import products from external source."""
        imported = 0
        for product in products:
            if "name" in product and "expiry" in product:
                await self.async_add_product(product)
                imported += 1
        return imported

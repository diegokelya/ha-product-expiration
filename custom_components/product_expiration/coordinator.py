"""Coordinator for Product Expiration."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import CONF_PHOTO_BASE_URL, CONF_WARN_DAYS, DEFAULT_SCAN_INTERVAL, DEFAULT_WARN_DAYS, DOMAIN
from .storage import ProductStorage

_LOGGER = logging.getLogger(__name__)


class ProductExpirationCoordinator(DataUpdateCoordinator):
    """Coordinator to manage product expiration data."""
    
    def __init__(self, hass: HomeAssistant, storage: ProductStorage, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.storage = storage
        self.entry = entry
    
    @property
    def warn_days(self) -> list[int]:
        """Get warning days from config."""
        return self.entry.options.get(
            CONF_WARN_DAYS,
            self.entry.data.get(CONF_WARN_DAYS, DEFAULT_WARN_DAYS)
        )
    
    @property
    def photo_base_url(self) -> str | None:
        """Get photo base URL from config."""
        return self.entry.options.get(
            CONF_PHOTO_BASE_URL,
            self.entry.data.get(CONF_PHOTO_BASE_URL)
        )
    
    @property
    def expiring_soon_threshold(self) -> int:
        """Get the threshold for 'expiring soon' based on warn_days.
        
        Uses the maximum configured warning period (≤15 days) so products
        appear in 'expiring_soon' throughout the entire warning window.
        Very long periods (>15 days) are for early alerts, not 'soon'.
        """
        if not self.warn_days:
            return 7
        # Filter to reasonable "soon" values (≤15 days) and take the largest
        candidates = sorted([d for d in self.warn_days if 1 <= d <= 15], reverse=True)
        return candidates[0] if candidates else 7
    
    def _build_image_url(self, image_filename: str | None) -> str | None:
        """Build full image URL from filename."""
        if not image_filename:
            return None
        
        base_url = self.photo_base_url
        if not base_url:
            return image_filename  # Return as-is if no base URL configured
        
        # Ensure base URL doesn't end with slash, filename doesn't start with one
        base_url = base_url.rstrip('/')
        image_filename = image_filename.lstrip('/')
        
        return f"{base_url}/{image_filename}"
    
    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from storage and process it."""
        try:
            products = self.storage.get_products()
            today = dt_util.now().date()
            
            expired = []
            expiring_soon = []
            upcoming = []
            errors = []
            
            for product in products:
                try:
                    # Parse expiry date safely
                    expiry_str = product.get("expiry")
                    if not expiry_str:
                        errors.append(f"Product {product.get('name', 'Unknown')} has no expiry date")
                        continue
                    
                    expiry_date = datetime.fromisoformat(expiry_str).date()
                    days_until = (expiry_date - today).days
                    
                    product_with_status = {
                        **product,
                        "days_until_expiry": days_until,
                        "status": self._get_status(days_until),
                        "image_url": self._build_image_url(product.get("image")),
                    }
                    
                    if days_until < 0:
                        expired.append(product_with_status)
                    elif days_until <= self.expiring_soon_threshold:
                        expiring_soon.append(product_with_status)
                    else:
                        upcoming.append(product_with_status)
                
                except (ValueError, TypeError) as err:
                    errors.append(f"Invalid date for {product.get('name', 'Unknown')}: {err}")
                    continue
            
            if errors:
                _LOGGER.warning("Product data errors: %s", "; ".join(errors))
            
            # Sort by expiry date
            all_products = sorted(
                expired + expiring_soon + upcoming,
                key=lambda p: p["expiry"]
            )
            
            # Find next expiry (first non-expired product)
            next_product = None
            next_expiry = None
            for product in all_products:
                if product["days_until_expiry"] >= 0:
                    next_product = product
                    next_expiry = product["expiry"]
                    break
            
            return {
                "products": all_products,
                "expired": expired,
                "expiring_soon": expiring_soon,
                "upcoming": upcoming,
                "next_product": next_product,
                "next_expiry": next_expiry,
                "total_count": len(all_products),
                "expired_count": len(expired),
                "expiring_soon_count": len(expiring_soon),
                "warn_days": self.warn_days,
                "photo_base_url": self.photo_base_url,
            }
        except Exception as err:
            raise UpdateFailed(f"Error fetching product data: {err}") from err
    
    def _get_status(self, days_until: int) -> dict[str, str]:
        """Get status label and icon based on days until expiry."""
        if days_until < 0:
            abs_days = abs(days_until)
            return {
                "label": f"🔴 Vencido hace {abs_days} día{'s' if abs_days != 1 else ''}",
                "icon": "mdi:alert-circle",
                "color": "red"
            }
        elif days_until == 0:
            return {
                "label": "🔴 Vence hoy",
                "icon": "mdi:alert",
                "color": "red"
            }
        elif days_until <= self.expiring_soon_threshold:
            return {
                "label": f"🟠 Vence en {days_until} día{'s' if days_until != 1 else ''}",
                "icon": "mdi:alert-circle-outline",
                "color": "orange"
            }
        else:
            return {
                "label": f"🟢 Vence en {days_until} días",
                "icon": "mdi:check-circle",
                "color": "green"
            }

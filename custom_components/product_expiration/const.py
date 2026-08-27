"""Constants for the Product Expiration Tracker integration."""

DOMAIN = "product_expiration"

# Configuration
CONF_WARN_DAYS = "warn_days"
CONF_PHOTO_BASE_URL = "photo_base_url"

# Defaults
DEFAULT_WARN_DAYS = [30, 15, 7, 3, 1]
DEFAULT_SCAN_INTERVAL = 3600  # 1 hour

# Storage
STORAGE_VERSION = 1
STORAGE_KEY = f"{DOMAIN}.storage"

# Attributes
ATTR_PRODUCTS = "products"
ATTR_EXPIRED = "expired"
ATTR_EXPIRING_SOON = "expiring_soon"
ATTR_NEXT_EXPIRY = "next_expiry"
ATTR_NEXT_PRODUCT = "next_product"
ATTR_DAYS_UNTIL_EXPIRY = "days_until_expiry"

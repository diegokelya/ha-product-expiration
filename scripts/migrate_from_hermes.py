#!/usr/bin/env python3
"""Copy existing inventory to the new integration format."""
import json
import shutil
from datetime import datetime
from pathlib import Path

# Source paths (current system)
SOURCE_JSON = Path("/home/diego/.hermes/data/vencimientos/products.json")
SOURCE_PHOTOS = Path("/home/diego/.hermes/data/vencimientos/fotos")

# Destination paths (Home Assistant config)
# Update these to match your HA config directory
HA_CONFIG = Path.home() / ".homeassistant"  # or wherever your config is
DEST_STORAGE = HA_CONFIG / ".storage" / "product_expiration.storage"
DEST_PHOTOS = HA_CONFIG / "www" / "product_photos"


def migrate_inventory():
    """Migrate from Hermes format to HA integration format."""
    print("Product Expiration Migration Tool")
    print("=" * 60)
    
    if not SOURCE_JSON.exists():
        print(f"❌ Source file not found: {SOURCE_JSON}")
        return
    
    # Read source
    with open(SOURCE_JSON) as f:
        source_data = json.load(f)
    
    products = source_data.get("products", [])
    print(f"✓ Found {len(products)} products in source")
    
    # Create destination directories
    DEST_PHOTOS.mkdir(parents=True, exist_ok=True)
    DEST_STORAGE.parent.mkdir(parents=True, exist_ok=True)
    
    # Copy photos
    if SOURCE_PHOTOS.exists():
        copied = 0
        for product in products:
            if "image" in product:
                src_photo = SOURCE_PHOTOS / product["image"]
                if src_photo.exists():
                    dest_photo = DEST_PHOTOS / product["image"]
                    shutil.copy2(src_photo, dest_photo)
                    copied += 1
        print(f"✓ Copied {copied} photos to {DEST_PHOTOS}")
    
    # Transform to HA storage format
    storage_data = {
        "version": 1,
        "key": "product_expiration.storage",
        "data": {
            "products": products
        }
    }
    
    # Backup existing if any
    if DEST_STORAGE.exists():
        backup = DEST_STORAGE.with_suffix(f".backup.{datetime.now():%Y%m%d_%H%M%S}")
        shutil.copy2(DEST_STORAGE, backup)
        print(f"✓ Backed up existing storage to {backup.name}")
    
    # Write new storage
    with open(DEST_STORAGE, "w") as f:
        json.dump(storage_data, f, indent=2)
    
    print(f"✓ Migrated storage to {DEST_STORAGE}")
    print("\n" + "=" * 60)
    print("Migration complete!")
    print("\nNext steps:")
    print("1. Restart Home Assistant")
    print("2. Go to Settings → Devices & Services → Add Integration")
    print("3. Search for 'Product Expiration Tracker'")
    print("4. Configure the photo base URL as:")
    print(f"   http://YOUR_HA_IP:8123/local/product_photos")
    print("\nThe integration will load your existing products automatically.")


if __name__ == "__main__":
    migrate_inventory()

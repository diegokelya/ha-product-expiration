#!/usr/bin/env python3
"""Import existing product inventory into Home Assistant Product Expiration integration."""
import argparse
import asyncio
import json
import sys
from pathlib import Path

# This script should be run from Home Assistant's config directory
# python3 scripts/import_existing_inventory.py /path/to/products.json


async def import_products(source_file: Path) -> None:
    """Import products from JSON file."""
    if not source_file.exists():
        print(f"Error: File not found: {source_file}")
        sys.exit(1)
    
    with open(source_file) as f:
        data = json.load(f)
    
    products = data.get("products", [])
    
    if not products:
        print("No products found in file")
        return
    
    print(f"Found {len(products)} products to import")
    print("\nProducts:")
    for product in products:
        print(f"  - {product.get('name')} (expires: {product.get('expiry')})")
    
    print("\n" + "="*60)
    print("To import these products into Home Assistant:")
    print("1. Install the Product Expiration integration")
    print("2. Add it via Settings → Devices & Services")
    print("3. Use the product_expiration.add_product service for each product")
    print("\nExample automation for bulk import:")
    print("="*60)
    print("""
automation:
  - alias: "Import Product Inventory"
    trigger:
      - platform: homeassistant
        event: start
    action:""")
    
    for product in products:
        service_data = {
            "name": product.get("name"),
            "expiry": product.get("expiry"),
        }
        
        optional_fields = ["image", "literal_text", "confidence", "barcode", 
                          "quantity", "category", "location"]
        for field in optional_fields:
            if field in product:
                service_data[field] = product[field]
        
        print(f"""
      - service: product_expiration.add_product
        data: {json.dumps(service_data, indent=10)}""")
    
    print("\n" + "="*60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Import products from JSON into Home Assistant"
    )
    parser.add_argument(
        "source_file",
        type=Path,
        help="Path to products.json file",
    )
    
    args = parser.parse_args()
    
    asyncio.run(import_products(args.source_file))


if __name__ == "__main__":
    main()

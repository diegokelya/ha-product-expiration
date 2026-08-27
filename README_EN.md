# Home Assistant Product Expiration Tracker

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/diegokelya/ha-product-expiration.svg)](https://github.com/diegokelya/ha-product-expiration/releases)
[![License](https://img.shields.io/github/license/diegokelya/ha-product-expiration.svg)](LICENSE)

Product expiration tracker for Home Assistant. Manage your inventory with expiration dates and get automatic alerts before products expire.

[🇪🇸 Versión en Español](README.md)

## ✨ Features

- **4 native Home Assistant sensors** with real-time data
- **Services** to add, update, and remove products via automations
- **Configurable warning days** — customize when to alert you (e.g., 30, 15, 7, 3, 1 days before)
- **Photo support** — image URLs in sensor attributes for display in Lovelace
- **Categorization** and storage location
- **Optional barcodes**
- **Bulk import** from JSON
- **HACS installation**

> **Note:** This integration provides sensors and services. Alerts are created through Home Assistant automations, and photos appear as URLs in sensor attributes for display in Lovelace cards.

## 📦 Installation

### Via HACS (recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click ⋮ (menu) → "Custom repositories"
4. Add: `https://github.com/diegokelya/ha-product-expiration`
5. Category: "Integration"
6. Search for "Product Expiration Tracker" and install
7. **Restart Home Assistant**

### Manual

1. Copy `custom_components/product_expiration` to `<config>/custom_components/`
2. Restart Home Assistant
3. Go to **Settings** → **Devices & Services** → **+ Add Integration**
4. Search for "Product Expiration Tracker"

## ⚙️ Configuration

1. **Settings** → **Devices & Services** → **+ Add Integration**
2. Search for "Product Expiration Tracker"
3. Configure:
   - **Photo base URL** (optional): `http://192.168.1.100:8765` or `/local/product_photos`
   - **Warning days**: `30,15,7,3,1` (comma-separated)

## 📊 Sensors

The integration automatically creates:

| Sensor | Description |
|--------|-------------|
| `sensor.product_expiration_total_products` | Total number of products |
| `sensor.product_expiration_expired_products` | Already expired products |
| `sensor.product_expiration_expiring_soon` | Products expiring soon |
| `sensor.product_expiration_next_expiry` | Name of the next product to expire |

Each sensor includes **detailed attributes** with complete product lists, IDs, dates, quantities, categories, and images.

## 🔧 Services

### `product_expiration.add_product`

```yaml
service: product_expiration.add_product
data:
  name: "Hellmann's Mayonnaise"
  expiry: "2027-02-14"
  image: "mayonnaise.jpg"
  quantity: 1
  category: "Condiments"
  location: "Pantry"
  barcode: "7790895001635"
  confidence: "high"
```

### `product_expiration.update_product`

```yaml
service: product_expiration.update_product
data:
  product_id: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  quantity: 2
  expiry: "2027-03-01"
```

### `product_expiration.remove_product`

```yaml
service: product_expiration.remove_product
data:
  product_id: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
```

### `product_expiration.import_products`

```yaml
service: product_expiration.import_products
data:
  products:
    - name: "Product 1"
      expiry: "2027-01-15"
      quantity: 2
    - name: "Product 2"
      expiry: "2027-02-20"
```

## 🤖 Automations

### Notification for products expiring soon

```yaml
automation:
  - alias: "Alert expiring products"
    trigger:
      - platform: state
        entity_id: sensor.product_expiration_expiring_soon
    condition:
      - condition: template
        value_template: "{{ trigger.to_state.state | int > 0 }}"
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "⚠️ Products expiring soon"
          message: >
            You have {{ trigger.to_state.state }} product(s) expiring soon:
            {% for product in trigger.to_state.attributes.products %}
            - {{ product.name }} ({{ product.days_until_expiry }} days)
            {% endfor %}
```

### Daily reminder

```yaml
automation:
  - alias: "Daily expiration reminder"
    trigger:
      - platform: time
        at: "09:00:00"
    condition:
      - condition: template
        value_template: "{{ states('sensor.product_expiration_next_expiry') not in ['unknown', 'unavailable'] }}"
    action:
      - service: notify.telegram
        data:
          message: >
            📅 Next expiration:
            {{ states('sensor.product_expiration_next_expiry') }}
            ({{ state_attr('sensor.product_expiration_next_expiry', 'days_until_expiry') }} days)
```

## 📸 Product Entry Workflows

### Telegram Bot (⚡ Recommended - 15 seconds)

Ultra-fast workflow via Telegram:

1. Send photo to bot
2. Reply with date (DD/MM/YY)
3. Product added automatically

```bash
cd examples/telegram-workflow
./install.sh
```

See [examples/telegram-workflow/README_EN.md](examples/telegram-workflow/README_EN.md) for complete instructions.

**Features:**
- ⚡ 15 seconds vs. 2-3 minutes with dashboard
- 📱 From any mobile device
- ✅ Immediate confirmation with days remaining
- ⚠️ Alert if product is already expired

### Simple Upload from HA Dashboard

Manual workflow with native YAML automations (no OCR):

```bash
cd examples/simple-upload
```

See [examples/simple-upload/README_EN.md](examples/simple-upload/README_EN.md)

**Features:**
- ✅ No external dependencies
- 📸 Snapshot from HA camera
- ⌨️ Manual date entry
- 📊 Visual preview before confirming

### Upload with OCR (advanced)

Complete workflow with automatic date extraction:

```bash
cd examples/upload-workflow
./install.sh
```

See [examples/upload-workflow/README.md](examples/upload-workflow/README.md)

**Features:**
- 🤖 Automatic OCR date extraction (pytesseract)
- 📋 Multiple formats: DD/MM/YY, EXP: DD/MM/YYYY, DD MONTH YYYY
- 📸 Snapshot from camera or manual upload

## 📤 Migration from existing system

If you have a previous `products.json`:

```bash
python3 scripts/import_existing_inventory.py /path/to/products.json
```

Generates YAML to copy into an automation that imports everything.

Or migrate directly with the complete script:

```bash
python3 scripts/migrate_from_hermes.py
```

## 📋 Example Dashboard

```yaml
type: vertical-stack
cards:
  - type: entities
    title: Expiration Summary
    entities:
      - sensor.product_expiration_total_products
      - sensor.product_expiration_expired_products
      - sensor.product_expiration_expiring_soon
      - sensor.product_expiration_next_expiry

  - type: markdown
    title: Products expiring soon
    content: |
      {% set products = state_attr('sensor.product_expiration_expiring_soon', 'products') %}
      {% if products %}
      {% for p in products[:5] %}
      - **{{ p.name }}**: {{ p.status }} ({{ p.expiry }})
      {% endfor %}
      {% else %}
      ✅ No products expiring soon
      {% endif %}
```

## 🧪 Development

```bash
# Clone
git clone https://github.com/diegokelya/ha-product-expiration
cd ha-product-expiration

# Tests (requires pytest)
pip3 install -r requirements_test.txt
pytest tests/

# Validate syntax
python3 -m py_compile custom_components/product_expiration/*.py
```

## 🤝 Contributing

1. Fork the project
2. Create a branch: `git checkout -b feature/new-feature`
3. Commit: `git commit -m 'Add new feature'`
4. Push: `git push origin feature/new-feature`
5. Open a Pull Request

## 📝 License

MIT License - see [LICENSE](LICENSE)

## 👤 Author

**Diego Kelyacoubian**

## 🐛 Support

[Report an issue](https://github.com/diegokelya/ha-product-expiration/issues)

---

**Note**: This integration stores data in `.storage/product_expiration.storage`. Changes persist between Home Assistant restarts.

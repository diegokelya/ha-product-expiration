# Product Expiration Tracker - Project Summary

## 🎯 Project Overview

Complete Home Assistant integration for managing product expiration dates with multiple entry workflows.

**Repository:** https://github.com/diegokelya/ha-product-expiration  
**Version:** 1.0.0  
**License:** MIT  
**Language:** Spanish + English

---

## 📦 What's Included

### Core Integration
- **Custom Component** (`custom_components/product_expiration/`)
  - 4 native sensors (total, expired, expiring soon, next expiry)
  - Services: add_product, update_product, remove_product, import_products
  - Photo support via URLs in sensor attributes
  - Configurable warning thresholds
  - Persistent storage (`.storage/product_expiration.storage`)

### Entry Workflows (3 options)

#### 1. Telegram Bot ⚡ (Recommended - 15 seconds)
- **Location:** `examples/telegram-workflow/`
- **Files:**
  - `telegram_product_bot.py` - Conversational bot
  - `install.sh` - Auto-installer
  - `telegram-product-bot.service` - systemd service
  - `README.md` / `README_EN.md` - Documentation

**Flow:**
1. Send photo to Telegram bot
2. Bot asks for expiration date
3. Reply with "DD/MM/YY"
4. Product added automatically

**Features:**
- Multi-format date parsing (DD/MM/YY, DD/MM/YYYY, ISO)
- Immediate alerts for expired products
- Photo storage in `~/photos/products/`
- Stateful conversation tracking
- Zero UI navigation

#### 2. Simple Dashboard Upload (No OCR)
- **Location:** `examples/simple-upload/`
- **Files:**
  - `automations.yaml` - Native HA automations
  - `helpers.yaml` - Input helpers config
  - `dashboard_card.yaml` - Lovelace card
  - `README.md` / `README_EN.md` - Documentation

**Flow:**
1. Point camera at product
2. Enter product name (triggers snapshot)
3. Select expiration date from picker
4. Product added

**Features:**
- 100% native YAML (no Python scripts)
- Visual preview before confirmation
- No external dependencies

#### 3. OCR Workflow (Advanced)
- **Location:** `examples/upload-workflow/`
- **Features:**
  - Automatic date extraction via pytesseract
  - Multiple format recognition
  - Manual fallback option

---

## 🔧 Technical Architecture

### Stack
- **Platform:** Home Assistant (2023.1.0+)
- **Language:** Python 3.11+
- **Storage:** JSON-based persistent storage
- **APIs:** 
  - Home Assistant Core API
  - Telegram Bot API (optional)
  - Home Assistant REST API

### Components

```
ha-product-expiration/
├── custom_components/product_expiration/
│   ├── __init__.py          # Integration entry, services
│   ├── sensor.py            # 4 sensors
│   ├── storage.py           # Persistent data layer
│   ├── coordinator.py       # Update coordinator
│   ├── config_flow.py       # Config UI
│   └── const.py             # Constants
├── examples/
│   ├── telegram-workflow/   # Telegram bot
│   ├── simple-upload/       # Dashboard workflow
│   └── upload-workflow/     # OCR workflow
├── .github/workflows/
│   └── validate.yml         # CI validation
├── hacs.json                # HACS metadata
├── README.md                # Spanish docs
└── README_EN.md             # English docs
```

### Data Model

**Product:**
```python
{
  "id": "uuid-v4",
  "name": "Product Name",
  "expiry": "2027-02-14",      # ISO date
  "image": "filename.jpg",
  "quantity": 1,
  "category": "Category",
  "location": "Storage Location",
  "barcode": "1234567890",
  "confidence": "alta|media|baja|confirmada por usuario",
  "literal_text": "Original OCR text"
}
```

### Services

| Service | Parameters | Description |
|---------|-----------|-------------|
| `product_expiration.add_product` | name, expiry, image?, quantity?, category?, location?, barcode?, confidence? | Add new product |
| `product_expiration.update_product` | product_id, name?, expiry?, quantity?, image?, category?, location? | Update existing product |
| `product_expiration.remove_product` | product_id | Remove product |
| `product_expiration.import_products` | products (list) | Bulk import |

### Sensors

| Sensor | State | Attributes |
|--------|-------|-----------|
| `sensor.product_expiration_total_products` | Count | `products[]` with full details |
| `sensor.product_expiration_expired_products` | Count | `products[]` filtered by expired |
| `sensor.product_expiration_expiring_soon` | Count | `products[]` within warning threshold |
| `sensor.product_expiration_next_expiry` | Product name | `days_until_expiry`, `expiry_date`, product details |

---

## 🚀 Deployment

### HACS Installation
1. HACS → Integrations → Custom Repositories
2. Add: `https://github.com/diegokelya/ha-product-expiration`
3. Category: Integration
4. Install & restart HA

### Telegram Bot Setup
```bash
cd examples/telegram-workflow
./install.sh
# Follow prompts for HA_TOKEN and TELEGRAM_BOT_TOKEN

# Run as service
sudo cp telegram-product-bot.service /etc/systemd/system/
sudo systemctl enable --now telegram-product-bot
```

### Configuration
1. Settings → Devices & Services → Add Integration
2. Search "Product Expiration Tracker"
3. Configure:
   - `photo_base_url`: `/local/product_photos` or HTTP URL
   - `warning_days`: `30,15,7,3,1`

---

## 📊 Workflow Comparison

| Feature | Telegram | Dashboard | OCR |
|---------|----------|-----------|-----|
| **Time** | 15 sec | 2-3 min | 1 min |
| **Device** | Mobile | Browser | Browser |
| **Setup Complexity** | Medium | Low | High |
| **Dependencies** | Telegram bot | None | pytesseract |
| **Date Entry** | Manual | Manual | Auto |
| **Accuracy** | 100% | 100% | ~80% |
| **Best For** | Daily use | Occasional | Bulk entry |

---

## 🔐 Security

### Credentials
- `HA_TOKEN` - Long-lived access token (stored in `~/.hermes/.env`)
- `TELEGRAM_BOT_TOKEN` - Bot API token (stored in `~/.hermes/.env`)

### Photo Storage
- Local: `~/photos/products/` (Telegram bot)
- HA: `/config/www/product_photos/` (Dashboard)
- Access: Photos served via `/local/` endpoint (HA authentication)

### Permissions
- Telegram bot: read-only to Telegram API, write to HA API
- Integration: read/write `.storage/product_expiration.storage`

---

## 🧪 Testing & CI

### GitHub Actions
- **Workflow:** `.github/workflows/validate.yml`
- **Triggers:** Push to main, PRs
- **Checks:**
  - Python syntax validation
  - Ruff linting (continue-on-error)

### Manual Testing
```bash
python3 -m py_compile custom_components/product_expiration/*.py
ruff check custom_components/product_expiration/
pytest tests/  # (requires test suite)
```

---

## 📈 Future Improvements

### Planned
1. **Smart Alerts** (Priority 3)
   - Daily digest via Telegram
   - Escalating warnings (7d, 3d, 1d, expired)
   - Customizable per-product thresholds

2. **Quick Actions** (Priority 2)
   - Telegram inline buttons: "Consumed", "-1", "+1"
   - Dashboard quick-delete buttons
   - `/exp list` command

3. **Auto-Categorization** (Priority 4)
   - Hardcoded dictionary: "mayonnaise" → "Condiments"
   - User training over time

4. **Enhanced Dashboard** (Priority 5)
   - `auto-entities` + `button-card` integration
   - Color coding: green >7d, yellow 3-7d, red <3d
   - Photo previews on tap

### Under Consideration
- Barcode scanning (mobile app integration)
- Shopping list integration
- Recipe ingredient tracking
- Multi-user support with per-user notifications
- Calendar view of expirations
- Export to CSV/PDF reports

---

## 📚 Documentation

### Available Languages
- 🇪🇸 Spanish (default)
- 🇬🇧 English

### Documentation Structure
```
README.md / README_EN.md              # Main docs
examples/telegram-workflow/
  ├── README.md                       # Spanish
  └── README_EN.md                    # English
examples/simple-upload/
  ├── README.md                       # Spanish
  └── README_EN.md                    # English
examples/upload-workflow/
  └── README.md                       # Spanish only
```

---

## 🤝 Contributing

### Process
1. Fork repository
2. Create feature branch: `git checkout -b feat/feature-name`
3. Commit: `git commit -m 'feat: description'`
4. Push: `git push origin feat/feature-name`
5. Open Pull Request

### Commit Convention
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation
- `chore:` - Maintenance
- `refactor:` - Code restructure

---

## 📞 Support

- **Issues:** https://github.com/diegokelya/ha-product-expiration/issues
- **Discussions:** GitHub Discussions (when enabled)
- **Documentation:** In-repo README files

---

## 📄 License

MIT License - Free for personal and commercial use.

---

## ✅ Release Checklist

- [x] Core integration implemented
- [x] 4 sensors working
- [x] Services (add, update, remove, import)
- [x] Telegram bot workflow
- [x] Simple dashboard workflow
- [x] OCR workflow
- [x] HACS metadata
- [x] GitHub Actions CI
- [x] English documentation
- [x] Spanish documentation
- [x] v1.0.0 release published
- [ ] HACS default repository submission
- [ ] Home Assistant Community Forum post
- [ ] Demo video/GIF
- [ ] Test suite

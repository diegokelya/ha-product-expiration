# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [2.0.0] - 2026-08-27

### 🚀 Major Release: Telegram Bot v2.0

#### Added

**OCR Automatic Date Detection**
- Automatic expiration date extraction from photos using Tesseract OCR
- ~80% accuracy rate on clear product photos
- Supports Spanish and English date formats
- Automatic fallback to manual entry if OCR fails or not installed
- Reduces workflow from 15 seconds to ~5 seconds

**Management Commands**
- `/venc lista` - List next 10 products by expiration date with color-coded urgency
- `/venc consumido <name>` - Delete product by name (fuzzy search)
- `/venc buscar <name>` - Search products by name with full details
- `/venc ayuda` - Built-in help and command reference
- All commands work without opening Home Assistant UI

**Auto-Categorization**
- Automatic product categorization based on name keywords
- 9 pre-configured categories: Condimentos, Panificados, Lácteos, Carnes, Verduras, Frutas, Almacén, Bebidas
- Zero user input required
- Categories shown in confirmation messages and search results

**Daily Expiration Alerts**
- Proactive morning summary (9:00 AM) via Telegram
- Grouped by urgency: Expired, Today, 1-3 days, 4-7 days
- Smart silence: only sends if there are products requiring attention
- Cron-based, runs independently of bot

**Documentation**
- `examples/telegram-workflow/README_V2.md` - Complete v2.0 documentation
- `examples/telegram-workflow/upgrade_to_v2.sh` - Automated upgrade script
- Updated README.md and README_EN.md with v2.0 features
- ROADMAP.md with 13 prioritized future improvements

#### Changed
- Bot now `telegram_product_bot_v2.py` (v1 remains available as backup)
- Workflow time: **15 seconds → 5 seconds** (with OCR)
- Product confirmation messages now include category if auto-detected
- Help system integrated into bot (no external docs needed for basic usage)

#### Technical Details
- OCR: pytesseract + Pillow + tesseract-ocr (optional dependencies)
- Date patterns: VTO, VENC, EXP prefixes + bare dates
- Fuzzy product search: case-insensitive substring matching
- State management: persistent JSON for conversation context

---

## [1.0.0] - 2026-08-26

### 🎉 Initial Release

#### Added

**Core Integration**
- Custom Home Assistant integration for product expiration tracking
- 4 native sensors: total_products, expired_products, expiring_soon, next_expiry
- Services: add_product, update_product, remove_product, import_products
- Persistent storage in `.storage/product_expiration.storage`
- Configurable warning thresholds (default: 30,15,7,3,1 days)
- Photo support via URL references

**Telegram Bot v1.0**
- Conversational photo upload workflow
- Manual date entry with multi-format parsing (DD/MM/YY, DD/MM/YYYY, ISO)
- Product name from photo caption or default
- Immediate feedback with days until expiry
- Alert if product already expired
- ~15 second workflow

**Dashboard Workflows**
- Simple Upload: Native YAML workflow with camera snapshot
- OCR Upload: Automatic date extraction with pytesseract
- Example dashboard cards with Lovelace

**Documentation**
- Bilingual docs: Spanish (README.md) + English (README_EN.md)
- Installation guides for all workflows
- HACS metadata for custom repository installation
- Migration scripts from existing JSON inventories
- Demo section with workflow examples

**Infrastructure**
- GitHub Actions CI: Python syntax validation + ruff linting
- Systemd service file for Telegram bot
- Installation scripts with dependency checking
- HACS compatible (custom repository)

#### Technical Details
- Platform: Home Assistant 2023.1.0+
- Python: 3.11+
- Storage: JSON-based (native HA storage)
- API: HA REST API + Telegram Bot API
- License: MIT

---

## Roadmap

See [ROADMAP.md](ROADMAP.md) for planned future improvements including:
- Visual search (photo matching)
- Shopping list integration
- Enhanced dashboard with auto-entities
- Barcode scanning
- Export/reporting features

---

## Links

- **Repository:** https://github.com/diegokelya/ha-product-expiration
- **Issues:** https://github.com/diegokelya/ha-product-expiration/issues
- **HACS:** Add as custom repository

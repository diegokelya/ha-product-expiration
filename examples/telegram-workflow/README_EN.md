# Telegram Workflow - Rapid Product Entry

Ultra-fast workflow to add products via Telegram Bot:

1. 📸 Send product photo to bot
2. ⌨️ Bot asks for date, you reply "DD/MM/YY"
3. ✅ Product automatically added with alert if expired

**Time:** ~15 seconds vs. 2-3 minutes with dashboard.

[🇪🇸 Versión en Español](README.md)

## Installation

### 1. Prerequisites

- Configured Telegram Bot (token)
- Home Assistant accessible via HTTP
- HA Long-Lived Access Token
- Python 3 with `requests` installed

### 2. Configure environment variables

Edit `~/.hermes/.env` or create a local `.env` file:

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
TELEGRAM_CHAT_ID="406287065"

# Home Assistant
HA_URL="http://homeassistant.local:8123"
HA_TOKEN="your_long_lived_access_token_here"
```

**Get HA Token:**
1. Home Assistant → User Profile (bottom left)
2. Scroll to 'Long-Lived Access Tokens'
3. "Create Token" → name "Telegram Product Bot"
4. Copy generated token

### 3. Install dependencies

```bash
pip3 install requests
# Or if using venv:
uv pip install requests
```

### 4. Make executable and test

```bash
chmod +x telegram_product_bot.py

# Test manually
python3 telegram_product_bot.py
```

Keep the script running and send a photo to the bot. It should respond asking for the date.

### 5. Run as service (optional)

**Option A: Via systemd (Linux)**

Create `/etc/systemd/system/telegram-product-bot.service`:

```ini
[Unit]
Description=Telegram Product Bot for Home Assistant
After=network.target

[Service]
Type=simple
User=diego
WorkingDirectory=/home/diego/projects/ha-product-expiration/examples/telegram-workflow
EnvironmentFile=/home/diego/.hermes/.env
ExecStart=/usr/bin/python3 /home/diego/projects/ha-product-expiration/examples/telegram-workflow/telegram_product_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Activate:

```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-product-bot
sudo systemctl start telegram-product-bot
sudo systemctl status telegram-product-bot
```

**Option B: Via Hermes cron job**

```bash
hermes cronjob create \
  --name "telegram-product-bot" \
  --script telegram_product_bot.py \
  --schedule "@reboot" \
  --no-agent
```

**Option C: Via terminal background in Hermes**

```python
# From a Hermes session
terminal(
    command="cd ~/projects/ha-product-expiration/examples/telegram-workflow && python3 telegram_product_bot.py",
    background=True
)
```

## Usage

### Basic workflow

1. **Send photo to bot:**
   - Open Telegram
   - Go to chat with your bot
   - Send product photo
   - (Optional) Add product name as caption

2. **Bot responds:**
   ```
   📸 Photo received: Product
   
   What is the expiration date?
   Valid formats: DD/MM/YY, DD/MM/YYYY, DD-MM-YY
   ```

3. **You reply with date:**
   ```
   08/25/26
   ```

4. **Bot confirms:**
   ```
   ✅ Product added
   
   📦 Name: Hellmann's Mayonnaise
   📅 Expiration: 08/25/2026
   ⏱ EXPIRES IN 45 DAYS
   ```

   Or if expired:
   ```
   ⚠️ Product added
   
   📦 Name: Bread
   📅 Expiration: 01/15/2026
   ⏱ EXPIRED 590 days ago
   ```

### Accepted date formats

- `08/25/26` → 2026-08-25
- `08/25/2026` → 2026-08-25
- `08-25-26` → 2026-08-25
- `2026-08-25` → 2026-08-25 (ISO)

### Adding product name

**Option 1:** Caption in photo (recommended)

```
[Photo] + "Hellmann's Mayonnaise with lemon"
```

**Option 2:** Edit later in HA dashboard

Product is added as "Product" if no caption, you can rename it later.

## Advantages vs. Dashboard

| Aspect | Telegram | HA Dashboard |
|---------|----------|--------------|
| Time | ~15 sec | 2-3 min |
| Device | Mobile phone | Browser/HA app |
| Steps | Photo → Date | Open HA → Capture → Field → Selector → Confirm |
| UI Navigation | Zero | Multiple |
| Confirmation | Immediate with days remaining | Visual in dashboard |
| Alerts | Same Telegram chat | Separate |

## Troubleshooting

### Bot doesn't respond

```bash
# Check bot is running
ps aux | grep telegram_product_bot

# View logs if in systemd
sudo journalctl -u telegram-product-bot -f

# Test manually
python3 telegram_product_bot.py
```

### Error "HA_TOKEN not set"

Verify `.env` file is in correct location with format:

```bash
HA_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

No spaces around `=`.

### Error adding product

- Verify Home Assistant is accessible from where bot runs
- Test service manually:

```bash
curl -X POST http://homeassistant.local:8123/api/services/product_expiration/add_product \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Product",
    "expiry": "2027-01-01",
    "image": "test.jpg"
  }'
```

### Photo not saved

Bot saves photos to `~/photos/products/`. Check permissions:

```bash
mkdir -p ~/photos/products
chmod 755 ~/photos/products
```

## Future improvements

- [ ] Automatic OCR date extraction (pytesseract)
- [ ] Inline buttons to confirm/edit date
- [ ] Auto-categorization by name
- [ ] Search for existing products
- [ ] `/exp list` command to view upcoming expirations
- [ ] Edit/delete via inline buttons

## Architecture

```
Telegram App
    ↓ [photo + caption]
Telegram Bot (polling)
    ↓ [download photo]
Local Storage (~/photos/products/)
    ↓ [ask date]
User
    ↓ [reply "DD/MM/YY"]
Date Parser
    ↓ [ISO date]
Home Assistant API
    ↓ [product_expiration.add_product]
Product Expiration Storage
    ↓ [update sensors]
Dashboard + Automations
```

## Code

See `telegram_product_bot.py` for complete implementation.

Conversational pattern:
- `load_state()` / `save_state()` for context between messages
- `handle_photo_message()` saves photo and asks for date
- `handle_text_message()` parses date and calls HA service
- `poll_updates()` infinite loop listening to bot API

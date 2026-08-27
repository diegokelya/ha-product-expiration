#!/bin/bash
# Upgrade Telegram Bot from v1 to v2
# Adds: OCR, commands, auto-categorization, daily alerts

set -e

WORKFLOW_DIR="$HOME/projects/ha-product-expiration/examples/telegram-workflow"

echo "=== Telegram Bot Upgrade v1 → v2 ==="
echo

# Check if project exists
if [ ! -d "$WORKFLOW_DIR" ]; then
    echo "❌ Project not found at $WORKFLOW_DIR"
    exit 1
fi

cd "$WORKFLOW_DIR"

# Backup v1
if [ -f "telegram_product_bot.py" ]; then
    echo "📦 Backing up v1..."
    cp telegram_product_bot.py telegram_product_bot_v1_backup.py
    echo "✅ Backup saved: telegram_product_bot_v1_backup.py"
fi

# Install OCR (optional)
echo
echo "🤖 OCR Installation (optional but recommended)"
echo
read -p "Install Tesseract OCR for automatic date detection? [Y/n] " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    echo "Installing Tesseract..."
    
    if command -v apt-get &>/dev/null; then
        sudo apt-get update
        sudo apt-get install -y tesseract-ocr tesseract-ocr-spa tesseract-ocr-eng
    else
        echo "⚠️  Manual installation required:"
        echo "   Ubuntu/Debian: sudo apt-get install tesseract-ocr"
        echo "   macOS: brew install tesseract"
    fi
    
    echo "Installing Python packages..."
    pip3 install pytesseract Pillow --quiet
    
    echo "✅ OCR installed"
else
    echo "⏭️  Skipping OCR (bot will use manual fallback)"
fi

# Activate v2
echo
echo "🔄 Activating bot v2..."
cp telegram_product_bot_v2.py telegram_product_bot.py
echo "✅ Bot v2 activated"

# Setup daily alerts cron
echo
echo "📅 Daily Alerts Setup"
echo
read -p "Configure daily expiration alerts (9:00 AM)? [Y/n] " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    # Check if cron exists
    if ! crontab -l 2>/dev/null | grep -q "telegram_daily_alerts.py"; then
        echo "Adding cron job..."
        
        # Add cron entry
        (crontab -l 2>/dev/null; echo "0 9 * * * cd $WORKFLOW_DIR && source ~/.hermes/.env && python3 telegram_daily_alerts.py >> /tmp/telegram_alerts.log 2>&1") | crontab -
        
        echo "✅ Daily alerts configured (9:00 AM)"
        echo "   Logs: /tmp/telegram_alerts.log"
    else
        echo "✅ Cron job already exists"
    fi
else
    echo "⏭️  Skipping daily alerts"
    echo "   To add later: crontab -e"
    echo "   0 9 * * * cd $WORKFLOW_DIR && source ~/.hermes/.env && python3 telegram_daily_alerts.py"
fi

# Restart service if running
echo
if systemctl is-active --quiet telegram-product-bot; then
    echo "🔄 Restarting bot service..."
    sudo systemctl restart telegram-product-bot
    echo "✅ Service restarted"
    
    echo
    echo "📊 Checking status..."
    sleep 2
    sudo systemctl status telegram-product-bot --no-pager --lines=5
else
    echo "ℹ️  Service not running. Start with:"
    echo "   sudo systemctl start telegram-product-bot"
fi

echo
echo "=== Upgrade Complete ==="
echo
echo "📋 What's New:"
echo "  ✅ OCR automatic date detection (if installed)"
echo "  ✅ /venc lista - List products"
echo "  ✅ /venc consumido <name> - Delete product"
echo "  ✅ /venc buscar <name> - Search products"
echo "  ✅ /venc ayuda - Help"
echo "  ✅ Auto-categorization"
echo "  ✅ Daily alerts (if configured)"
echo
echo "🧪 Test:"
echo "  1. Send photo to bot"
echo "  2. If OCR enabled: bot detects date automatically"
echo "  3. Try: /venc ayuda"
echo
echo "📖 Docs: $WORKFLOW_DIR/README_V2.md"
echo

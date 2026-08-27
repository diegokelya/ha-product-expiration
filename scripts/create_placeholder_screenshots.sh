#!/bin/bash
# Helper script to create placeholder screenshots for testing layout

set -e

IMG_DIR="docs/images"
mkdir -p "$IMG_DIR"

echo "Creating placeholder screenshots..."

# Check if ImageMagick is installed
if ! command -v convert &>/dev/null; then
    echo "ImageMagick not found. Installing..."
    if command -v apt-get &>/dev/null; then
        sudo apt-get update && sudo apt-get install -y imagemagick
    else
        echo "Please install ImageMagick manually:"
        echo "  Ubuntu/Debian: sudo apt-get install imagemagick"
        echo "  macOS: brew install imagemagick"
        exit 1
    fi
fi

# Create placeholder images with text
create_placeholder() {
    local filename=$1
    local text=$2
    local width=${3:-800}
    local height=${4:-600}
    
    convert -size ${width}x${height} xc:"#2c3e50" \
        -pointsize 24 -fill white \
        -gravity center -annotate +0+0 "$text" \
        -pointsize 14 -fill "#95a5a6" \
        -gravity south -annotate +0+50 "Placeholder - Replace with actual screenshot" \
        "$IMG_DIR/$filename"
    
    echo "✓ Created $filename"
}

# Create all placeholder screenshots
create_placeholder "telegram-workflow-demo.png" "Telegram Bot Workflow\n\n📸 User sends photo\n⏬\n🤖 Bot: What's the expiration date?\n⏬\n👤 User: 25/08/26\n⏬\n✅ Product added, expires in 45 days"
create_placeholder "dashboard-overview.png" "Home Assistant Dashboard\n\n📊 Total Products: 5\n❌ Expired: 0\n⚠️ Expiring Soon: 2\n📅 Next: Mayonnaise (45 days)"
create_placeholder "simple-upload-flow.png" "Simple Upload Workflow\n\n📷 Camera Preview\n📝 Product Name: _______\n📅 Expiration Date: [  /  /  ]\n[Add Product]"
create_placeholder "product-card.png" "Product Detail Card\n\n[Product Photo]\nHellmann's Mayonnaise\nExpires: 2026-08-25\n⏱ 45 days remaining\n[Consumed] [-1] [+1]" 400 500
create_placeholder "notification-mobile.png" "Mobile Notification\n\n⚠️ Products Expiring Soon\n\nYou have 2 products expiring:\n• Mayonnaise (7 days)\n• Bread (3 days)" 400 600
create_placeholder "hacs-install.png" "HACS Installation\n\nCustom Repositories\n\nProduct Expiration Tracker\n by Diego Kelyacoubian\n[Install] [Info]"

echo
echo "✅ All placeholder screenshots created in $IMG_DIR/"
echo
echo "To replace with real screenshots:"
echo "  1. Take actual screenshots following docs/SCREENSHOTS.md"
echo "  2. Name them exactly as the placeholders"
echo "  3. Overwrite files in $IMG_DIR/"
echo "  4. Run: git add docs/images/*.png && git commit -m 'docs: add real screenshots'"
echo

# Screenshot Guide for Product Expiration Tracker

This guide lists all screenshots needed for the documentation.

## Required Screenshots

### 1. Telegram Workflow Demo

**File:** `docs/images/telegram-workflow-demo.png`

**How to capture:**
1. Open Telegram on mobile
2. Take a screenshot showing the full conversation:
   - User sends product photo
   - Bot asks for expiration date
   - User replies "25/08/26"
   - Bot confirms with green checkmark and product details

**Recommended tool:** Phone screenshot or Telegram Desktop

---

### 2. HA Dashboard with Products

**File:** `docs/images/dashboard-overview.png`

**How to capture:**
1. Open Home Assistant dashboard
2. Navigate to Product Expiration dashboard
3. Show:
   - 4 main sensors (total, expired, expiring soon, next expiry)
   - List of products with photos
   - Color coding (green/yellow/red based on days remaining)

**URL:** `http://homeassistant.local:8123/lovelace/products`

---

### 3. Simple Upload Workflow

**File:** `docs/images/simple-upload-flow.png`

**How to capture:**
1. Open HA dashboard with simple upload card
2. Show the input fields:
   - Product name input
   - Photo preview
   - Date picker
   - Add button

---

### 4. Product Detail Card

**File:** `docs/images/product-card.png`

**How to capture:**
1. Single product card showing:
   - Product photo
   - Name
   - Expiration date
   - Days remaining (with color)
   - Quick action buttons (if implemented)

---

### 5. Mobile Notification

**File:** `docs/images/notification-mobile.png`

**How to capture:**
1. Trigger expiration alert
2. Screenshot of mobile notification showing:
   - Alert icon
   - Product name
   - Days until expiration
   - Photo thumbnail (if supported)

---

### 6. Telegram Bot States

**File:** `docs/images/telegram-bot-states.png`

**How to capture:**
Combined screenshot showing:
1. Initial state (send photo prompt)
2. Waiting for date state
3. Success confirmation
4. Error handling (invalid date format)

---

### 7. HACS Installation

**File:** `docs/images/hacs-install.png`

**How to capture:**
1. HACS → Integrations → Custom Repositories
2. Show Product Expiration Tracker in the list
3. Install button visible

---

## How to Add Screenshots

### 1. Take the screenshots following the guide above

### 2. Optimize images
```bash
# Install imagemagick if needed
sudo apt-get install imagemagick

# Resize and optimize (max width 800px)
mogrify -resize 800x -quality 85 docs/images/*.png

# Or use online tools:
# - https://tinypng.com/
# - https://squoosh.app/
```

### 3. Add to git
```bash
cd ~/projects/ha-product-expiration
git add docs/images/*.png
git commit -m "docs: add demo screenshots"
git push
```

### 4. Update documentation
The README files are already configured to display images. Once you add the files, they will appear automatically.

---

## Placeholder Creation (for testing)

If you want to test the layout before taking real screenshots, create placeholders:

```bash
# Create placeholder images (requires imagemagick)
convert -size 800x600 xc:gray -pointsize 30 -draw "text 250,300 'Telegram Workflow Demo'" docs/images/telegram-workflow-demo.png
convert -size 800x600 xc:gray -pointsize 30 -draw "text 250,300 'Dashboard Overview'" docs/images/dashboard-overview.png
convert -size 800x600 xc:gray -pointsize 30 -draw "text 250,300 'Simple Upload Flow'" docs/images/simple-upload-flow.png
```

---

## Alternative: GIF Animations

For even better documentation, consider creating short GIFs:

**Tools:**
- **Peek** (Linux): https://github.com/phw/peek
- **LICEcap** (Windows/Mac): https://www.cockos.com/licecap/
- **ScreenToGif** (Windows): https://www.screentogif.com/

**Example GIFs to create:**
1. `telegram-workflow.gif` - Full Telegram workflow in action
2. `dashboard-add-product.gif` - Adding product from dashboard
3. `hacs-install.gif` - HACS installation process

```bash
# Optimize GIFs
gifsicle -O3 --colors 256 -o docs/images/telegram-workflow-optimized.gif docs/images/telegram-workflow.gif
```

---

## Current Status

- [ ] Telegram workflow demo
- [ ] Dashboard overview
- [ ] Simple upload flow
- [ ] Product detail card
- [ ] Mobile notification
- [ ] Telegram bot states
- [ ] HACS installation

Once screenshots are added, update this checklist.

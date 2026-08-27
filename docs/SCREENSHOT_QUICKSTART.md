# Quick Guide: Taking Screenshots for Documentation

## 🎯 Goal
Add visual demos to make the documentation more engaging and clear.

## 📋 Priority Screenshots (5 minutes each)

### 1️⃣ Telegram Workflow (HIGHEST PRIORITY)

**File:** `docs/images/telegram-workflow-demo.png`

**Steps:**
1. Start the Telegram bot (if not running):
   ```bash
   cd ~/projects/ha-product-expiration/examples/telegram-workflow
   source ~/.hermes/.env
   python3 telegram_product_bot.py &
   ```

2. On your phone:
   - Open Telegram
   - Go to your bot chat
   - Take photo of any product (or use existing photo)
   - Send it
   - Reply with date when asked
   - Wait for confirmation

3. Take screenshot showing the full conversation

4. Transfer to computer and save as:
   ```bash
   ~/projects/ha-product-expiration/docs/images/telegram-workflow-demo.png
   ```

**Alternative:** Use Telegram Desktop on computer for easier screenshot.

---

### 2️⃣ Home Assistant Sensors

**File:** `docs/images/dashboard-overview.png`

**Steps:**
1. Open `http://homeassistant.local:8123`
2. Go to Developer Tools → States
3. Filter by `product_expiration`
4. Screenshot showing all 4 sensors with values
5. Save as `docs/images/dashboard-overview.png`

**Better alternative:** If you've created a dashboard:
1. Screenshot the full dashboard with product cards
2. Shows sensors + product list with photos

---

### 3️⃣ Mobile Notification (if configured)

**File:** `docs/images/notification-mobile.png`

**Steps:**
1. Add a product expiring in 7 days (to trigger alert)
2. Wait for automation to fire notification
3. Screenshot the notification on phone
4. Transfer to `docs/images/notification-mobile.png`

**Skip if:** Alerts not configured yet — can add later

---

## 🚀 Quick Upload to GitHub

Once you have 1-3 screenshots:

```bash
cd ~/projects/ha-product-expiration

# Add images
git add docs/images/*.png

# Commit
git commit -m "docs: add demo screenshots"

# Push
git push
```

The images will automatically appear in the documentation!

---

## ✅ What Gets Updated Automatically

When you add images to `docs/images/`, these files will display them:

- ✅ `README.md` - Shows Telegram demo
- ✅ `README_EN.md` - Shows Telegram demo
- ✅ `docs/DEMO.md` - Shows all screenshots

No manual editing needed — the markdown references are already in place.

---

## 🎨 Optional: Image Optimization

If images are large (>500KB), optimize them:

**Online tools (no install needed):**
- https://tinypng.com/ (drag & drop)
- https://squoosh.app/ (web-based)

**Or via CLI:**
```bash
# Install optipng
sudo apt-get install optipng

# Optimize all PNGs
optipng -o5 docs/images/*.png
```

Target: ~200-300KB per screenshot

---

## 📝 Screenshot Checklist

- [ ] Telegram workflow demo (phone or desktop)
- [ ] HA dashboard with sensors
- [ ] Mobile notification (optional)
- [ ] Simple upload card (optional)
- [ ] Product detail card (optional)

**Minimum viable:** Just the Telegram workflow demo will make a huge difference!

---

## 🎥 Alternative: Screen Recording

Instead of screenshots, record a 30-second video:

**Tools:**
- **Peek** (Linux): Simple screen recorder
- **OBS Studio** (all platforms): Professional recording
- **Phone screen record** (iOS/Android built-in)

**Upload to:**
- YouTube (unlisted)
- GitHub release assets
- Imgur / Imgbb

Then embed in README:
```markdown
[![Demo Video](thumbnail.png)](https://www.youtube.com/watch?v=VIDEO_ID)
```

---

## ⏱ Estimated Time

- **1 screenshot (Telegram):** 5 minutes
- **3 screenshots:** 15 minutes
- **Full set (6 screenshots):** 30 minutes
- **Video demo:** 10 minutes recording + 5 minutes upload

**Recommended:** Start with just Telegram screenshot — biggest impact, least effort.

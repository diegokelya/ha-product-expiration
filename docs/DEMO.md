# Demo Screenshots - Product Expiration Tracker

**Note:** Screenshots will be added once the system is fully deployed and tested.

## Telegram Workflow Demo

![Telegram Bot Workflow](images/telegram-workflow-demo.png)

**What it shows:**
- User sends product photo to Telegram bot
- Bot responds: "📸 Photo received. What is the expiration date?"
- User replies: "25/08/26"
- Bot confirms: "✅ Product added - Hellmann's Mayonnaise - Expires: 08/25/2026 - ⏱ EXPIRES IN 45 DAYS"

---

## Home Assistant Dashboard

![Dashboard Overview](images/dashboard-overview.png)

**What it shows:**
- Overview card with 4 sensors:
  - Total Products: 5
  - Expired: 0
  - Expiring Soon: 2
  - Next Expiry: Mayonnaise (45 days)
- Product list with photos and color-coded status
- Green (>7 days), Yellow (3-7 days), Red (<3 days)

---

## Simple Upload Workflow

![Simple Upload Flow](images/simple-upload-flow.png)

**What it shows:**
- Camera preview pointing at product
- Input field: "Product Name"
- Photo thumbnail preview
- Date picker widget
- "Add Product" button

---

## Product Detail Card

![Product Card](images/product-card.png)

**What it shows:**
- Product photo (Hellmann's Mayonnaise)
- Product name
- Expiration date: 2026-08-25
- Days remaining: 45 days (green badge)
- Quick action buttons: [Consumed] [-1] [+1]

---

## Mobile Notification

![Mobile Notification](images/notification-mobile.png)

**What it shows:**
- Android/iOS notification
- Title: "⚠️ Products Expiring Soon"
- Body: "You have 2 products expiring: • Mayonnaise (7 days) • Bread (3 days)"
- Product photo thumbnail

---

## HACS Installation

![HACS Install](images/hacs-install.png)

**What it shows:**
- HACS Integrations page
- "Custom repositories" section
- Product Expiration Tracker listed
- Install button
- Repository info

---

## To Add Real Screenshots

1. Follow the guide in `SCREENSHOTS.md`
2. Replace placeholder descriptions with actual images
3. Run:
   ```bash
   git add docs/images/*.png
   git commit -m "docs: add real screenshots"
   git push
   ```

---

## Alternative: Video Demo

Consider creating a short video demo:
- **Platform:** YouTube, Vimeo, or Loom
- **Duration:** 1-2 minutes
- **Content:**
  - Quick overview of all 3 workflows
  - Live demo of Telegram bot
  - Dashboard interaction
  - Alert notification

Embed in README with:
```markdown
[![Demo Video](https://img.youtube.com/vi/VIDEO_ID/maxresdefault.jpg)](https://www.youtube.com/watch?v=VIDEO_ID)
```

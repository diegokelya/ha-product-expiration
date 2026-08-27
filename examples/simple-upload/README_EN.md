# Simple Photo Upload (NO OCR)

Workflow to add products with photo from Home Assistant **without installing additional dependencies**.

[🇪🇸 Versión en Español](README.md)

## Difference from OCR workflow

- ❌ Does NOT require pytesseract, tesseract-ocr, or Python scripts
- ✅ Only uses native HA YAML automations
- 📸 Take photo with camera
- ⌨️ Manually enter date you see in photo
- ✅ Product added with photo

## Installation

### 1. Create folder for photos

Via File Editor in Home Assistant:

Create folder: `/config/www/product_photos/`

### 2. Create helpers

**Settings → Devices & Services → Helpers → Create helper:**

1. **Input Text** - `product_name_capture`
   - Name: "Capture Product"
   - Max: 255

2. **Input Text** - `product_name_confirm`
   - Name: "Confirm Product"
   - Max: 255

3. **Input Text** - `current_photo_file`
   - Name: "Current Photo File"
   - Max: 255

4. **Input DateTime** - `product_expiry_date`
   - Name: "Expiration Date"
   - Date: YES
   - Time: NO

### 3. Add automations

Copy contents of `automations.yaml` to your `/config/automations.yaml`

Or create 2 automations via UI:
- "Product: Capture photo"
- "Product: Add with photo"

### 4. Configure photo_base_url

**Settings → Devices & Services → Product Expiration Tracker → Configure**

- `photo_base_url`: `/local/product_photos`

### 5. Add dashboard card

Copy contents of `dashboard_card.yaml` to your Lovelace dashboard.

### 6. Restart HA

**Settings → System → Restart Home Assistant**

## Usage

1. **Step 1: Capture photo**
   - Point `camera.entrada` at product
   - Write product name in "Capture Product"
   - Snapshot taken automatically when you write the name

2. **Step 2: Enter date**
   - Photo preview appears
   - Look at expiration date in photo
   - Select date in selector
   - Product automatically added

3. **Result**
   - Product added to `sensor.product_expiration_total_products`
   - Photo available in `/local/product_photos/`
   - Visible in dashboard with image

## Advantages

- ✅ No external dependencies
- ✅ No additional add-ons
- ✅ Works on any HA installation
- ✅ 100% native YAML
- ✅ Visual confirmation before adding

## Disadvantages

- ⌨️ Manual date entry (not automatic)
- 📸 One photo at a time

## Troubleshooting

### Photo not taken

- Verify `camera.entrada` is working
- Try `camera.snapshot` manually in Developer Tools

### Photo doesn't appear in dashboard

- Verify `/config/www/product_photos/` exists
- Check `photo_base_url` in integration: `/local/product_photos`
- Refresh browser (Ctrl+F5)

### Product not added

- Verify all 4 helpers are created
- Check logs in Settings → System → Logs
- Ensure Product Expiration integration is loaded

## Future improvement: Telegram

If you want to add products from Telegram (photo + automatic text), you can combine this workflow with the Telegram bot you already have configured.

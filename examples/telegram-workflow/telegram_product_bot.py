#!/usr/bin/env python3
"""
Telegram bot for adding products via photo + manual date entry.
Workflow:
1. User sends photo to bot
2. Bot asks for expiry date
3. User replies with date (DD/MM/AA or DD/MM/YYYY)
4. Bot calls HA service to add product
5. Bot confirms with product details
"""

import requests
import json
import os
import sys
from datetime import datetime
import re

# Configuration from environment or defaults
HA_URL = os.getenv("HA_URL", "http://homeassistant.local:8123")
HA_TOKEN = os.getenv("HA_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "406287065")

# State file to track conversation context
STATE_FILE = os.path.expanduser("~/.hermes/data/telegram_product_state.json")

def load_state():
    """Load conversation state."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_state(state):
    """Save conversation state."""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def download_photo(file_id):
    """Download photo from Telegram and save locally."""
    # Get file path
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile"
    resp = requests.get(url, params={"file_id": file_id})
    resp.raise_for_status()
    file_path = resp.json()["result"]["file_path"]
    
    # Download file
    download_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
    photo_resp = requests.get(download_url)
    photo_resp.raise_for_status()
    
    # Save with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"product_{timestamp}.jpg"
    local_path = os.path.expanduser(f"~/photos/products/{filename}")
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    
    with open(local_path, 'wb') as f:
        f.write(photo_resp.content)
    
    return filename

def send_telegram_message(text):
    """Send message via Telegram Bot API."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    resp = requests.post(url, json=data)
    resp.raise_for_status()
    return resp.json()

def parse_date(date_str):
    """Parse date from various formats: DD/MM/AA, DD/MM/YYYY, DD-MM-AA, etc."""
    # Clean input
    date_str = date_str.strip()
    
    # Try different patterns
    patterns = [
        (r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', '%d/%m/%Y'),  # DD/MM/YYYY or DD-MM-YYYY
        (r'(\d{1,2})[/-](\d{1,2})[/-](\d{2})', '%d/%m/%y'),   # DD/MM/YY or DD-MM-YY
        (r'(\d{4})-(\d{2})-(\d{2})', '%Y-%m-%d'),             # YYYY-MM-DD (ISO)
    ]
    
    for pattern, fmt in patterns:
        match = re.search(pattern, date_str)
        if match:
            try:
                # Reconstruct date string for parsing
                if fmt == '%d/%m/%Y' or fmt == '%d/%m/%y':
                    date_str_clean = f"{match.group(1)}/{match.group(2)}/{match.group(3)}"
                else:
                    date_str_clean = match.group(0)
                
                parsed = datetime.strptime(date_str_clean, fmt)
                return parsed.strftime('%Y-%m-%d')
            except ValueError:
                continue
    
    return None

def call_ha_add_product(name, expiry_date, image_filename):
    """Call Home Assistant service to add product."""
    url = f"{HA_URL}/api/services/product_expiration/add_product"
    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "name": name,
        "expiry": expiry_date,
        "image": image_filename,
        "confidence": "confirmada por usuario",
        "quantity": 1
    }
    
    resp = requests.post(url, headers=headers, json=data)
    resp.raise_for_status()
    return resp.json()

def handle_photo_message(message):
    """Handle incoming photo message."""
    state = load_state()
    
    # Get largest photo
    photos = message.get('photo', [])
    if not photos:
        return
    
    largest_photo = max(photos, key=lambda p: p['file_size'])
    file_id = largest_photo['file_id']
    
    # Download photo
    filename = download_photo(file_id)
    
    # Extract caption as product name (if provided)
    caption = message.get('caption', '').strip()
    product_name = caption if caption else "Producto"
    
    # Save state
    state[str(message['from']['id'])] = {
        'waiting_for': 'expiry_date',
        'photo_filename': filename,
        'product_name': product_name
    }
    save_state(state)
    
    # Ask for expiry date
    send_telegram_message(
        f"📸 Foto recibida: *{product_name}*\n\n"
        f"¿Cuál es la fecha de vencimiento?\n"
        f"Formatos válidos: DD/MM/AA, DD/MM/YYYY, DD-MM-AA"
    )

def handle_text_message(message):
    """Handle incoming text message."""
    state = load_state()
    user_id = str(message['from']['id'])
    text = message.get('text', '').strip()
    
    if user_id not in state:
        send_telegram_message(
            "👋 Envíame una foto del producto para empezar.\n"
            "Podés incluir el nombre en la descripción de la foto."
        )
        return
    
    user_state = state[user_id]
    
    if user_state.get('waiting_for') == 'expiry_date':
        # Parse date
        expiry_date = parse_date(text)
        
        if not expiry_date:
            send_telegram_message(
                "❌ No pude entender la fecha.\n\n"
                "Por favor enviá en formato: DD/MM/AA o DD/MM/YYYY\n"
                "Ejemplo: 25/08/26 o 25/08/2026"
            )
            return
        
        # Check if date is in the past
        expiry_dt = datetime.strptime(expiry_date, '%Y-%m-%d')
        days_until = (expiry_dt - datetime.now()).days
        
        # Call HA service
        try:
            call_ha_add_product(
                user_state['product_name'],
                expiry_date,
                user_state['photo_filename']
            )
            
            # Format confirmation
            status_emoji = "⚠️" if days_until <= 7 else "✅"
            status_text = f"VENCE EN {days_until} DÍAS" if days_until > 0 else f"VENCIDO hace {abs(days_until)} días"
            
            send_telegram_message(
                f"{status_emoji} *Producto agregado*\n\n"
                f"📦 Nombre: {user_state['product_name']}\n"
                f"📅 Vencimiento: {expiry_dt.strftime('%d/%m/%Y')}\n"
                f"⏱ {status_text}"
            )
            
            # Clear state
            del state[user_id]
            save_state(state)
            
        except Exception as e:
            send_telegram_message(
                f"❌ Error al agregar producto:\n{str(e)}\n\n"
                f"Verificá que Home Assistant esté accesible."
            )

def poll_updates(offset=0):
    """Poll for Telegram updates."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    params = {
        "offset": offset,
        "timeout": 30,
        "allowed_updates": ["message"]
    }
    
    resp = requests.get(url, params=params, timeout=35)
    resp.raise_for_status()
    return resp.json()

def main():
    """Main bot loop."""
    # Validate config
    if not TELEGRAM_BOT_TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN not set", file=sys.stderr)
        sys.exit(1)
    if not HA_TOKEN:
        print("ERROR: HA_TOKEN not set", file=sys.stderr)
        sys.exit(1)
    
    print(f"Telegram Product Bot started")
    print(f"Listening for messages in chat {TELEGRAM_CHAT_ID}...")
    
    offset = 0
    
    while True:
        try:
            result = poll_updates(offset)
            
            for update in result.get('result', []):
                offset = update['update_id'] + 1
                
                message = update.get('message')
                if not message:
                    continue
                
                # Only process messages from configured chat
                if str(message['chat']['id']) != str(TELEGRAM_CHAT_ID):
                    continue
                
                # Handle photo
                if 'photo' in message:
                    handle_photo_message(message)
                
                # Handle text
                elif 'text' in message:
                    handle_text_message(message)
        
        except KeyboardInterrupt:
            print("\nBot stopped by user")
            break
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            import time
            time.sleep(5)

if __name__ == '__main__':
    main()

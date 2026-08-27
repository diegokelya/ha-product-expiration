#!/usr/bin/env python3
"""
Telegram bot for product expiration tracking.

Features:
- Photo upload with OCR date extraction (optional fallback to manual)
- Commands: /venc lista, /venc consumido, /venc buscar, /venc ayuda
- Auto-categorization
- Conversational state management

Version: 2.0 (with commands + OCR)
"""

import requests
import json
import os
import sys
from datetime import datetime
import re

# Optional OCR support
try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# Configuration
HA_URL = os.getenv("HA_URL", "http://homeassistant.local:8123")
HA_TOKEN = os.getenv("HA_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "406287065")

STATE_FILE = os.path.expanduser("~/.hermes/data/telegram_product_state.json")

# Auto-categorization mapping
CATEGORY_MAPPING = {
    "mayonesa|ketchup|mostaza|salsa|aderezo": "Condimentos",
    "pan|tostadas|galletas|medialunas|factura|tortilla": "Panificados",
    "leche|yogur|queso|manteca|crema|dulce de leche": "Lácteos",
    "pollo|carne|pescado|chorizo|salchicha|jamón": "Carnes",
    "tomate|lechuga|papa|cebolla|zanahoria|acelga": "Verduras",
    "manzana|banana|naranja|pera|uva|frutilla": "Frutas",
    "arroz|fideos|harina|polenta|lentejas": "Almacén",
    "coca|sprite|fanta|jugo|agua|gaseosa": "Bebidas",
}

def auto_categorize(product_name):
    """Auto-categorize product based on name."""
    name_lower = product_name.lower()
    for keywords, category in CATEGORY_MAPPING.items():
        if any(kw in name_lower for kw in keywords.split("|")):
            return category
    return None

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

def download_photo(file_id, return_path=False):
    """Download photo from Telegram and save locally."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile"
    resp = requests.get(url, params={"file_id": file_id})
    resp.raise_for_status()
    file_path = resp.json()["result"]["file_path"]
    
    download_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
    photo_resp = requests.get(download_url)
    photo_resp.raise_for_status()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"product_{timestamp}.jpg"
    local_path = os.path.expanduser(f"~/photos/products/{filename}")
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    
    with open(local_path, 'wb') as f:
        f.write(photo_resp.content)
    
    if return_path:
        return filename, local_path
    return filename

def send_telegram_message(text, parse_mode="Markdown"):
    """Send message via Telegram Bot API."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": parse_mode
    }
    resp = requests.post(url, json=data)
    resp.raise_for_status()
    return resp.json()

def extract_date_from_image(image_path):
    """Extract expiration date from image using OCR."""
    if not OCR_AVAILABLE:
        return None
    
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang='spa+eng')
        
        # Common patterns in Spanish/English
        patterns = [
            r'VTO[:\s]*(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
            r'VENC[:\s]*(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
            r'EXP[:\s]*(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                day = match.group(1)
                month = match.group(2)
                year = match.group(3)
                
                # Normalize year
                if len(year) == 2:
                    year = f"20{year}"
                
                try:
                    parsed = datetime.strptime(f"{day}/{month}/{year}", '%d/%m/%Y')
                    return parsed.strftime('%Y-%m-%d'), f"{day}/{month}/{year}"
                except ValueError:
                    continue
        
        return None
    except Exception as e:
        print(f"OCR error: {e}", file=sys.stderr)
        return None

def parse_date(date_str):
    """Parse date from various formats."""
    date_str = date_str.strip()
    
    patterns = [
        (r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', '%d/%m/%Y'),
        (r'(\d{1,2})[/-](\d{1,2})[/-](\d{2})', '%d/%m/%y'),
        (r'(\d{4})-(\d{2})-(\d{2})', '%Y-%m-%d'),
    ]
    
    for pattern, fmt in patterns:
        match = re.search(pattern, date_str)
        if match:
            try:
                if fmt == '%d/%m/%Y' or fmt == '%d/%m/%y':
                    date_str_clean = f"{match.group(1)}/{match.group(2)}/{match.group(3)}"
                else:
                    date_str_clean = match.group(0)
                
                parsed = datetime.strptime(date_str_clean, fmt)
                return parsed.strftime('%Y-%m-%d')
            except ValueError:
                continue
    
    return None

def get_all_products():
    """Get all products from HA sensor."""
    url = f"{HA_URL}/api/states/sensor.product_expiration_total_products"
    headers = {"Authorization": f"Bearer {HA_TOKEN}"}
    
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    return data.get('attributes', {}).get('products', [])

def call_ha_add_product(name, expiry_date, image_filename, category=None, confidence="confirmada por usuario"):
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
        "confidence": confidence,
        "quantity": 1
    }
    
    if category:
        data["category"] = category
    
    resp = requests.post(url, headers=headers, json=data)
    resp.raise_for_status()
    return resp.json()

def call_ha_remove_product(product_id):
    """Call HA service to remove product."""
    url = f"{HA_URL}/api/services/product_expiration/remove_product"
    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {"product_id": product_id}
    
    resp = requests.post(url, headers=headers, json=data)
    resp.raise_for_status()
    return resp.json()

def handle_command_lista(args):
    """Handle /venc lista command."""
    try:
        products = get_all_products()
        
        if not products:
            send_telegram_message("📦 No hay productos registrados.")
            return
        
        # Sort by days remaining
        products_sorted = sorted(products, key=lambda p: p.get('days_until_expiry', 999))
        
        # Limit to 10
        limit = 10
        message_lines = [f"📋 *Próximos {min(len(products_sorted), limit)} vencimientos:*\n"]
        
        for i, p in enumerate(products_sorted[:limit], 1):
            name = p.get('name', 'Producto')
            days = p.get('days_until_expiry', 0)
            expiry = p.get('expiry', '')
            
            if days < 0:
                emoji = "🔴"
                status = f"VENCIDO hace {abs(days)} días"
            elif days == 0:
                emoji = "⚠️"
                status = "VENCE HOY"
            elif days <= 3:
                emoji = "🟠"
                status = f"vence en {days} días"
            elif days <= 7:
                emoji = "🟡"
                status = f"vence en {days} días"
            else:
                emoji = "🟢"
                status = f"vence en {days} días"
            
            message_lines.append(f"{i}. {emoji} *{name}*")
            message_lines.append(f"   {status} ({expiry})")
        
        if len(products_sorted) > limit:
            message_lines.append(f"\n... y {len(products_sorted) - limit} más")
        
        message_lines.append(f"\n📊 Total: {len(products)} productos")
        
        send_telegram_message("\n".join(message_lines))
    
    except Exception as e:
        send_telegram_message(f"❌ Error al listar productos: {str(e)}")

def handle_command_consumido(args):
    """Handle /venc consumido <name> command."""
    if not args:
        send_telegram_message("❌ Uso: /venc consumido <nombre o parte del nombre>")
        return
    
    try:
        search_term = " ".join(args).lower()
        products = get_all_products()
        
        # Find matching products
        matches = [p for p in products if search_term in p.get('name', '').lower()]
        
        if not matches:
            send_telegram_message(f"❌ No encontré productos con: *{search_term}*")
            return
        
        if len(matches) > 1:
            message_lines = [f"🔍 Encontré {len(matches)} productos:\n"]
            for i, p in enumerate(matches[:5], 1):
                message_lines.append(f"{i}. {p.get('name')}")
            message_lines.append(f"\nEspecificá mejor el nombre.")
            send_telegram_message("\n".join(message_lines))
            return
        
        # Remove product
        product = matches[0]
        call_ha_remove_product(product['id'])
        
        send_telegram_message(
            f"✅ *Producto eliminado*\n\n"
            f"📦 {product.get('name')}\n"
            f"📅 Vencía: {product.get('expiry')}"
        )
    
    except Exception as e:
        send_telegram_message(f"❌ Error: {str(e)}")

def handle_command_buscar(args):
    """Handle /venc buscar <name> command."""
    if not args:
        send_telegram_message("❌ Uso: /venc buscar <nombre>")
        return
    
    try:
        search_term = " ".join(args).lower()
        products = get_all_products()
        
        matches = [p for p in products if search_term in p.get('name', '').lower()]
        
        if not matches:
            send_telegram_message(f"❌ No encontré productos con: *{search_term}*")
            return
        
        message_lines = [f"🔍 *Resultados para: {search_term}*\n"]
        
        for p in matches[:5]:
            name = p.get('name', 'Producto')
            days = p.get('days_until_expiry', 0)
            expiry = p.get('expiry', '')
            category = p.get('category', '')
            
            if days < 0:
                emoji = "🔴"
                status = f"VENCIDO hace {abs(days)} días"
            elif days <= 7:
                emoji = "⚠️"
                status = f"vence en {days} días"
            else:
                emoji = "🟢"
                status = f"vence en {days} días"
            
            message_lines.append(f"{emoji} *{name}*")
            message_lines.append(f"   {status} ({expiry})")
            if category:
                message_lines.append(f"   🏷️ {category}")
            message_lines.append("")
        
        if len(matches) > 5:
            message_lines.append(f"... y {len(matches) - 5} más")
        
        send_telegram_message("\n".join(message_lines))
    
    except Exception as e:
        send_telegram_message(f"❌ Error: {str(e)}")

def handle_command_ayuda(args):
    """Handle /venc ayuda command."""
    help_text = """
🤖 *Comandos Disponibles*

📸 *Agregar producto:*
Enviá foto del producto (con nombre opcional como caption)

📋 *Comandos:*
`/venc lista` - Lista próximos vencimientos
`/venc consumido <nombre>` - Elimina producto
`/venc buscar <nombre>` - Busca productos
`/venc ayuda` - Esta ayuda

💡 *Ejemplos:*
`/venc consumido mayonesa`
`/venc buscar queso`
    """
    send_telegram_message(help_text.strip())

def handle_command(text):
    """Handle /venc commands."""
    parts = text.strip().split()
    
    if len(parts) == 1:
        # Just /venc - show help
        handle_command_ayuda([])
        return True
    
    command = parts[1].lower()
    args = parts[2:] if len(parts) > 2 else []
    
    if command == "lista":
        handle_command_lista(args)
    elif command == "consumido":
        handle_command_consumido(args)
    elif command == "buscar":
        handle_command_buscar(args)
    elif command == "ayuda" or command == "help":
        handle_command_ayuda(args)
    else:
        send_telegram_message(f"❌ Comando desconocido: {command}\n\nEnviá /venc ayuda para ver comandos.")
    
    return True

def handle_photo_message(message):
    """Handle incoming photo message with OCR."""
    state = load_state()
    
    photos = message.get('photo', [])
    if not photos:
        return
    
    largest_photo = max(photos, key=lambda p: p['file_size'])
    file_id = largest_photo['file_id']
    
    # Download photo
    filename, local_path = download_photo(file_id, return_path=True)
    
    # Extract caption as product name
    caption = message.get('caption', '').strip()
    product_name = caption if caption else "Producto"
    
    # Try OCR if available
    ocr_result = None
    if OCR_AVAILABLE:
        ocr_result = extract_date_from_image(local_path)
    
    user_id = str(message['from']['id'])
    
    if ocr_result:
        # OCR found a date
        iso_date, readable_date = ocr_result
        
        # Save state for confirmation
        state[user_id] = {
            'waiting_for': 'ocr_confirmation',
            'photo_filename': filename,
            'product_name': product_name,
            'ocr_date_iso': iso_date,
            'ocr_date_readable': readable_date
        }
        save_state(state)
        
        send_telegram_message(
            f"📸 Foto recibida: *{product_name}*\n\n"
            f"🤖 Detecté vencimiento: *{readable_date}*\n\n"
            f"¿Es correcto? Respondé:\n"
            f"• *Sí* o *s* para confirmar\n"
            f"• La fecha correcta (ej: 25/08/26)"
        )
    else:
        # OCR not available or failed - fallback to manual
        state[user_id] = {
            'waiting_for': 'expiry_date',
            'photo_filename': filename,
            'product_name': product_name
        }
        save_state(state)
        
        ocr_msg = " (OCR no disponible)" if not OCR_AVAILABLE else ""
        send_telegram_message(
            f"📸 Foto recibida: *{product_name}*{ocr_msg}\n\n"
            f"¿Cuál es la fecha de vencimiento?\n"
            f"Formatos: DD/MM/AA, DD/MM/YYYY, DD-MM-AA"
        )

def handle_text_message(message):
    """Handle incoming text message."""
    state = load_state()
    user_id = str(message['from']['id'])
    text = message.get('text', '').strip()
    
    # Check for commands
    if text.lower().startswith('/venc'):
        handle_command(text)
        return
    
    if user_id not in state:
        send_telegram_message(
            "👋 Enviame una foto del producto para empezar.\n\n"
            "O usá /venc ayuda para ver comandos."
        )
        return
    
    user_state = state[user_id]
    
    # Handle OCR confirmation
    if user_state.get('waiting_for') == 'ocr_confirmation':
        if text.lower() in ['si', 'sí', 's', 'yes', 'ok']:
            # Use OCR date
            expiry_date = user_state['ocr_date_iso']
            add_product_and_confirm(user_state, expiry_date, user_id, state, confidence="OCR + confirmada")
        else:
            # Manual date provided
            expiry_date = parse_date(text)
            if not expiry_date:
                send_telegram_message(
                    "❌ No pude entender la fecha.\n\n"
                    "Formato: DD/MM/AA o DD/MM/YYYY\n"
                    "Ejemplo: 25/08/26"
                )
                return
            add_product_and_confirm(user_state, expiry_date, user_id, state)
    
    # Handle manual date entry
    elif user_state.get('waiting_for') == 'expiry_date':
        expiry_date = parse_date(text)
        
        if not expiry_date:
            send_telegram_message(
                "❌ No pude entender la fecha.\n\n"
                "Formato: DD/MM/AA o DD/MM/YYYY\n"
                "Ejemplo: 25/08/26"
            )
            return
        
        add_product_and_confirm(user_state, expiry_date, user_id, state)

def add_product_and_confirm(user_state, expiry_date, user_id, state, confidence="confirmada por usuario"):
    """Add product to HA and send confirmation."""
    expiry_dt = datetime.strptime(expiry_date, '%Y-%m-%d')
    days_until = (expiry_dt - datetime.now()).days
    
    # Auto-categorize
    category = auto_categorize(user_state['product_name'])
    
    try:
        call_ha_add_product(
            user_state['product_name'],
            expiry_date,
            user_state['photo_filename'],
            category=category,
            confidence=confidence
        )
        
        status_emoji = "⚠️" if days_until <= 7 else "✅"
        status_text = f"VENCE EN {days_until} DÍAS" if days_until > 0 else f"VENCIDO hace {abs(days_until)} días"
        
        category_line = f"\n🏷️ Categoría: {category}" if category else ""
        
        send_telegram_message(
            f"{status_emoji} *Producto agregado*\n\n"
            f"📦 Nombre: {user_state['product_name']}\n"
            f"📅 Vencimiento: {expiry_dt.strftime('%d/%m/%Y')}\n"
            f"⏱ {status_text}{category_line}"
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
    if not TELEGRAM_BOT_TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN not set", file=sys.stderr)
        sys.exit(1)
    if not HA_TOKEN:
        print("ERROR: HA_TOKEN not set", file=sys.stderr)
        sys.exit(1)
    
    ocr_status = "✅ enabled" if OCR_AVAILABLE else "❌ disabled (install: pip install pytesseract pillow)"
    print(f"Telegram Product Bot v2.0 started")
    print(f"OCR: {ocr_status}")
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
                
                if str(message['chat']['id']) != str(TELEGRAM_CHAT_ID):
                    continue
                
                if 'photo' in message:
                    handle_photo_message(message)
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

#!/usr/bin/env python3
"""
Daily expiration alerts via Telegram.
Sends proactive summary of products expiring soon.

Run as cron job: daily at 9:00 AM
"""

import requests
import json
import os
import sys
from datetime import datetime, date

# Configuration
HA_URL = os.getenv("HA_URL", "http://homeassistant.local:8123")
HA_TOKEN = os.getenv("HA_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "406287065")

def get_sensor_data(sensor_id):
    """Get sensor state from Home Assistant."""
    url = f"{HA_URL}/api/states/{sensor_id}"
    headers = {"Authorization": f"Bearer {HA_TOKEN}"}
    
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

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

def format_product_list(products, emoji, max_items=5):
    """Format product list with emoji."""
    lines = []
    for i, p in enumerate(products[:max_items]):
        name = p.get('name', 'Producto')
        days = p.get('days_until_expiry', 0)
        lines.append(f"{emoji} {name} ({abs(days)} días)")
    
    if len(products) > max_items:
        lines.append(f"   ... y {len(products) - max_items} más")
    
    return "\n".join(lines)

def main():
    """Send daily expiration alert."""
    # Validate config
    if not TELEGRAM_BOT_TOKEN or not HA_TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN or HA_TOKEN not set", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Get sensor data
        total_sensor = get_sensor_data("sensor.product_expiration_total_products")
        expired_sensor = get_sensor_data("sensor.product_expiration_expired_products")
        expiring_sensor = get_sensor_data("sensor.product_expiration_expiring_soon")
        next_sensor = get_sensor_data("sensor.product_expiration_next_expiry")
        
        total = int(total_sensor['state'])
        expired_count = int(expired_sensor['state'])
        expiring_count = int(expiring_sensor['state'])
        
        # Skip if nothing to report
        if expired_count == 0 and expiring_count == 0:
            print("No products expiring soon or expired. Skipping notification.")
            return
        
        # Build message
        message_lines = ["🌅 *Resumen de Vencimientos*\n"]
        
        # Expired products
        if expired_count > 0:
            expired_products = expired_sensor['attributes'].get('products', [])
            message_lines.append(f"🔴 *{expired_count} VENCIDO(S)*")
            message_lines.append(format_product_list(expired_products, "  •"))
            message_lines.append("")
        
        # Expiring soon
        if expiring_count > 0:
            expiring_products = expiring_sensor['attributes'].get('products', [])
            
            # Group by urgency
            today = []
            soon_3d = []
            soon_7d = []
            
            for p in expiring_products:
                days = p.get('days_until_expiry', 999)
                if days == 0:
                    today.append(p)
                elif days <= 3:
                    soon_3d.append(p)
                elif days <= 7:
                    soon_7d.append(p)
            
            if today:
                message_lines.append(f"⚠️ *{len(today)} VENCE(N) HOY*")
                message_lines.append(format_product_list(today, "  •"))
                message_lines.append("")
            
            if soon_3d:
                message_lines.append(f"🟠 *{len(soon_3d)} vence(n) en 1-3 días*")
                message_lines.append(format_product_list(soon_3d, "  •"))
                message_lines.append("")
            
            if soon_7d:
                message_lines.append(f"🟡 *{len(soon_7d)} vence(n) en 4-7 días*")
                message_lines.append(format_product_list(soon_7d, "  •"))
                message_lines.append("")
        
        # Summary
        message_lines.append(f"📊 Total: {total} productos")
        message_lines.append(f"\n_Enviá /venc para ver comandos_")
        
        message = "\n".join(message_lines)
        
        # Send alert
        send_telegram_message(message)
        print(f"Alert sent: {expired_count} expired, {expiring_count} expiring soon")
    
    except Exception as e:
        print(f"Error sending alert: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()

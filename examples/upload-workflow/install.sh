#!/bin/bash
# Script de instalación del workflow de upload de fotos
# Ejecutar en Home Assistant via SSH o terminal add-on

set -e

echo "=== Instalando workflow de upload de fotos ==="

# 1. Crear carpeta para fotos
echo "Creando carpeta /config/www/product_photos..."
mkdir -p /config/www/product_photos
chmod 755 /config/www/product_photos

# 2. Crear carpeta python_scripts
echo "Creando carpeta /config/python_scripts..."
mkdir -p /config/python_scripts

# 3. Copiar script OCR
echo "Copiando script OCR..."
cp ocr_expiry_date.py /config/python_scripts/

# 4. Instalar dependencias (solo si pip está disponible)
if command -v pip3 &> /dev/null; then
    echo "Instalando pytesseract y Pillow..."
    pip3 install --no-cache-dir pytesseract pillow
else
    echo "⚠️  pip3 no disponible - instalá manualmente: pip3 install pytesseract pillow"
fi

# 5. Verificar tesseract-ocr
if ! command -v tesseract &> /dev/null; then
    echo "⚠️  tesseract-ocr no instalado"
    echo "Instalá con: apk add tesseract-ocr tesseract-ocr-data-spa"
    echo "O en Debian/Ubuntu: apt-get install tesseract-ocr tesseract-ocr-spa"
fi

# 6. Crear helpers via REST API (requiere long-lived access token)
if [ -n "$HA_TOKEN" ]; then
    echo "Creando input helpers..."
    
    # input_text.product_photo_name
    curl -X POST -H "Authorization: Bearer $HA_TOKEN" \
         -H "Content-Type: application/json" \
         -d '{"name": "product_photo_name", "icon": "mdi:text", "initial": "", "max": 255}' \
         http://homeassistant.local:8123/api/config/input_text
    
    # input_text.product_last_photo
    curl -X POST -H "Authorization: Bearer $HA_TOKEN" \
         -H "Content-Type: application/json" \
         -d '{"name": "product_last_photo", "icon": "mdi:image", "initial": "", "max": 255}' \
         http://homeassistant.local:8123/api/config/input_text
    
    echo "Helpers creados ✓"
else
    echo "⚠️  Variable HA_TOKEN no configurada - creá los helpers manualmente"
fi

# 7. Instrucciones finales
cat <<EOF

✅ Instalación completa

Próximos pasos:

1. Habilitá python_script en configuration.yaml:
   
   python_script:

2. Agregá las automatizaciones de automations.yaml a tu config

3. Agregá la card de dashboard_card.yaml a tu Lovelace

4. Configurá photo_base_url en la integración:
   - Ajustes → Dispositivos y servicios → Product Expiration Tracker
   - Opciones → photo_base_url: /local/product_photos

5. Reiniciá Home Assistant

6. Probá tomando una foto desde el dashboard

EOF

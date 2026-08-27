"""OCR de fecha de vencimiento desde foto de producto.

Extrae la fecha de vencimiento de una imagen usando pytesseract OCR,
detecta patrones comunes (DD/MM/YY, VTO: DD/MM/YYYY, etc.) y
agrega el producto al tracker automáticamente.

Requisitos:
- pip3 install pytesseract pillow
- tesseract-ocr instalado en el sistema

Uso desde automatización:
  service: python_script.ocr_expiry_date
  data:
    image_path: "/config/www/product_photos/imagen.jpg"
    product_name: "Nombre del producto"
"""

import re
from datetime import datetime, timedelta
from pathlib import Path

try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logger.error("pytesseract o PIL no disponible. Instalá: pip3 install pytesseract pillow")

# Obtener parámetros
image_path = data.get("image_path")
product_name = data.get("product_name", "Producto sin nombre")

if not image_path:
    logger.error("Falta parámetro image_path")
else:
    if not OCR_AVAILABLE:
        logger.error("OCR no disponible - instalá dependencias")
    else:
        try:
            # Cargar imagen
            img_path = Path(image_path)
            if not img_path.exists():
                logger.error(f"Archivo no encontrado: {image_path}")
            else:
                img = Image.open(img_path)
                
                # Extraer texto con OCR
                text = pytesseract.image_to_string(img, lang='spa')
                logger.info(f"OCR detectó: {text}")
                
                # Patrones de fecha de vencimiento
                patterns = [
                    # VTO: 25/08/26, VTO 25/08/26, VENC: 25/08/26
                    r'V(?:TO|ENC)[:\s]*(\d{1,2})[/\-](\d{1,2})[/\-](\d{2,4})',
                    # 25/08/26, 25-08-26
                    r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{2,4})',
                    # EXP: 2026-08-25
                    r'EXP[:\s]*(\d{4})[/\-](\d{1,2})[/\-](\d{1,2})',
                    # CONSUME ANTES DEL 25 AGO 2026
                    r'(\d{1,2})\s+(ENE|FEB|MAR|ABR|MAY|JUN|JUL|AGO|SEP|OCT|NOV|DIC)[A-Z]*\s+(\d{2,4})',
                ]
                
                months_es = {
                    'ENE': 1, 'FEB': 2, 'MAR': 3, 'ABR': 4,
                    'MAY': 5, 'JUN': 6, 'JUL': 7, 'AGO': 8,
                    'SEP': 9, 'OCT': 10, 'NOV': 11, 'DIC': 12
                }
                
                expiry_date = None
                literal_text = None
                confidence = "baja"
                
                for pattern in patterns:
                    match = re.search(pattern, text.upper())
                    if match:
                        literal_text = match.group(0)
                        groups = match.groups()
                        
                        # Detectar formato y parsear
                        if any(month in groups[1] if len(groups) > 1 else '' for month in months_es.keys()):
                            # Formato: DD MES YYYY
                            day = int(groups[0])
                            month = months_es.get(groups[1][:3], 1)
                            year = int(groups[2])
                        elif len(groups[0]) == 4:
                            # Formato ISO: YYYY-MM-DD
                            year = int(groups[0])
                            month = int(groups[1])
                            day = int(groups[2])
                        else:
                            # Formato: DD/MM/YY o DD/MM/YYYY
                            day = int(groups[0])
                            month = int(groups[1])
                            year = int(groups[2])
                        
                        # Normalizar año (26 → 2026)
                        if year < 100:
                            year += 2000
                        
                        try:
                            expiry_date = f"{year:04d}-{month:02d}-{day:02d}"
                            
                            # Validar que la fecha sea razonable (no más de 5 años en el futuro)
                            parsed_date = datetime.strptime(expiry_date, "%Y-%m-%d")
                            if parsed_date > datetime.now() + timedelta(days=5*365):
                                logger.warning(f"Fecha sospechosa (>5 años): {expiry_date}")
                                confidence = "baja"
                            else:
                                confidence = "alta"
                            
                            break
                        except ValueError:
                            logger.warning(f"Fecha inválida: {day}/{month}/{year}")
                            continue
                
                if expiry_date:
                    # Generar ID único
                    product_id = f"{product_name.lower().replace(' ', '-')}-{expiry_date.replace('-', '')}"
                    filename = img_path.name
                    
                    # Llamar al servicio add_product
                    service_data = {
                        "name": product_name,
                        "expiry": expiry_date,
                        "image": filename,
                        "literal_text": literal_text,
                        "confidence": confidence,
                    }
                    
                    hass.services.call(
                        "product_expiration",
                        "add_product",
                        service_data,
                        blocking=True
                    )
                    
                    logger.info(f"Producto agregado: {product_name} - Vence: {expiry_date} (confianza: {confidence})")
                else:
                    logger.warning(f"No se detectó fecha de vencimiento en la imagen. Texto OCR: {text[:200]}")
                    
        except Exception as e:
            logger.error(f"Error procesando imagen: {e}")

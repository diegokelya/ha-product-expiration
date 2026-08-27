# Upload de Fotos desde Home Assistant

Este workflow permite subir fotos de productos desde el frontend de Home Assistant y agregarlas automáticamente al tracker con OCR de fecha de vencimiento.

## Arquitectura

```
Usuario toma foto con cámara/teléfono
    ↓
Snapshot guardado en /config/www/product_photos/
    ↓
Automatización detecta nuevo archivo
    ↓
Script Python extrae fecha de vencimiento (OCR)
    ↓
Llama product_expiration.add_product con imagen y fecha
```

## Instalación

### 1. Crear carpeta para fotos

Conectate a tu Home Assistant y ejecutá:

```bash
mkdir -p /config/www/product_photos
chmod 755 /config/www/product_photos
```

### 2. Agregar helpers en HA

**Ajustes → Dispositivos y servicios → Helpers → Crear helper**

- **Input Text:** `input_text.product_photo_name`
  - Nombre: "Nombre del producto"
  - Modo: texto

- **Input Text:** `input_text.product_last_photo`
  - Nombre: "Última foto subida"
  - Modo: texto

### 3. Configurar cámara o file upload

**Opción A: Usar snapshot de cámara existente**

Si ya tenés una cámara configurada (ej: `camera.entrada`):

```yaml
# configuration.yaml
camera:
  - platform: generic
    name: "Producto Scanner"
    still_image_url: "http://192.168.68.xxx/snapshot.jpg"
```

**Opción B: Crear input para upload manual**

Usaremos shell_command para mover archivos que subas manualmente a `/config/www/`.

### 4. Instalar dependencias OCR

Conectate a tu Home Assistant:

```bash
# Instalar pytesseract para OCR
pip3 install pytesseract pillow
# O si usás Home Assistant OS con add-ons:
apk add tesseract-ocr tesseract-ocr-data-spa
```

### 5. Copiar script de OCR

Copiá el archivo `ocr_expiry_date.py` a `/config/python_scripts/`:

```bash
mkdir -p /config/python_scripts
cp ocr_expiry_date.py /config/python_scripts/
```

Habilitá python_script en `configuration.yaml`:

```yaml
python_script:
```

### 6. Agregar automatizaciones

Copiá el contenido de `automations.yaml` a tu archivo de automatizaciones.

### 7. Agregar dashboard card

Copiá el contenido de `dashboard_card.yaml` a tu Lovelace dashboard.

## Uso

### Método 1: Snapshot de cámara

1. Apuntá la cámara al producto
2. Andá al dashboard "Agregar Producto"
3. Ingresá el nombre del producto
4. Presioná "Tomar Foto y Escanear"
5. El sistema extrae la fecha automáticamente y agrega el producto

### Método 2: Upload manual

1. Subí una foto a `/config/www/product_photos/` por SAMBA/SSH
2. El sistema detecta el archivo nuevo automáticamente
3. Extrae la fecha y agrega el producto

## Troubleshooting

### OCR no detecta la fecha

- Asegurate que la foto esté enfocada en la fecha de vencimiento
- Mejorá la iluminación
- Probá con diferentes ángulos
- Editá el script `ocr_expiry_date.py` para ajustar patrones de regex

### El servicio python_script no está disponible

- Verificá que `python_script:` esté en `configuration.yaml`
- Reiniciá Home Assistant

### Las fotos no se muestran en el dashboard

- Verificá que `photo_base_url` esté configurado como `/local/product_photos` en la integración
- Verificá permisos de `/config/www/product_photos/` (755)

## Integración con visión AI (opcional)

Para mejorar la detección, podés usar Google Vision API o similar:

```yaml
# configuration.yaml
google_assistant_sdk:
  project_id: tu-proyecto
  service_account: !include SERVICE_ACCOUNT.json
```

Esto permitiría detección más robusta de fechas en diferentes formatos.

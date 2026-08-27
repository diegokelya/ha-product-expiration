# Upload Simple de Fotos (SIN OCR)

Workflow para agregar productos con foto desde Home Assistant **sin instalar dependencias adicionales**.

## Diferencia con el workflow OCR

- ❌ NO requiere pytesseract, tesseract-ocr, ni Python scripts
- ✅ Solo usa automatizaciones YAML nativas de HA
- 📸 Tomás foto con cámara
- ⌨️ Ingresás manualmente la fecha que ves en la foto
- ✅ Producto agregado con foto

## Instalación

### 1. Crear carpeta para fotos

Via File Editor en Home Assistant:

Crear carpeta: `/config/www/product_photos/`

### 2. Crear helpers

**Ajustes → Dispositivos y servicios → Helpers → Crear helper:**

1. **Input Text** - `product_name_capture`
   - Nombre: "Capturar Producto"
   - Máximo: 255

2. **Input Text** - `product_name_confirm`
   - Nombre: "Confirmar Producto"
   - Máximo: 255

3. **Input Text** - `current_photo_file`
   - Nombre: "Archivo Foto Actual"
   - Máximo: 255

4. **Input DateTime** - `product_expiry_date`
   - Nombre: "Fecha Vencimiento"
   - Fecha: SÍ
   - Hora: NO

### 3. Agregar automatizaciones

Copiá el contenido de `automations.yaml` a tu `/config/automations.yaml`

O creá 2 automatizaciones via UI:
- "Producto: Capturar foto"
- "Producto: Agregar con foto"

### 4. Configurar photo_base_url

**Ajustes → Dispositivos y servicios → Product Expiration Tracker → Configurar**

- `photo_base_url`: `/local/product_photos`

### 5. Agregar dashboard card

Copiá el contenido de `dashboard_card.yaml` a tu dashboard Lovelace.

### 6. Reiniciar HA

**Ajustes → Sistema → Reiniciar Home Assistant**

## Uso

1. **Paso 1: Capturar foto**
   - Apuntá `camera.entrada` al producto
   - Escribí el nombre del producto en "Capturar Producto"
   - Se toma snapshot automáticamente cuando escribís el nombre

2. **Paso 2: Ingresar fecha**
   - Aparece preview de la foto capturada
   - Mirá la fecha de vencimiento en la foto
   - Seleccioná la fecha en el selector
   - Automáticamente se agrega el producto

3. **Resultado**
   - Producto agregado a `sensor.product_expiration_total_products`
   - Foto disponible en `/local/product_photos/`
   - Visible en dashboard con imagen

## Ventajas

- ✅ Sin dependencias externas
- ✅ Sin add-ons adicionales
- ✅ Funciona en cualquier instalación de HA
- ✅ 100% nativo YAML
- ✅ Confirmación visual antes de agregar

## Desventajas

- ⌨️ Ingreso manual de fecha (no automático)
- 📸 Una foto a la vez

## Troubleshooting

### La foto no se toma

- Verificá que `camera.entrada` esté funcionando
- Probá `camera.snapshot` manualmente en Herramientas de desarrollo

### La foto no aparece en el dashboard

- Verificá que `/config/www/product_photos/` exista
- Chequeá `photo_base_url` en la integración: `/local/product_photos`
- Refrescá el navegador (Ctrl+F5)

### El producto no se agrega

- Verificá que los 4 helpers estén creados
- Chequeá logs en Ajustes → Sistema → Registros
- Asegurate que la integración Product Expiration esté cargada

## Mejora futura: Telegram

Si querés agregar productos desde Telegram (foto + texto automático), podés combinar este workflow con el bot de Telegram que ya tenés configurado.

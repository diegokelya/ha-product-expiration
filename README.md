# Home Assistant Product Expiration Tracker

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/diegokelya/ha-product-expiration.svg)](https://github.com/diegokelya/ha-product-expiration/releases)
[![License](https://img.shields.io/github/license/diegokelya/ha-product-expiration.svg)](LICENSE)

Rastreador de vencimiento de productos para Home Assistant. Gestiona un inventario con fechas de vencimiento y te alerta automáticamente antes de que caduquen.

[🇬🇧 English version](README_EN.md)

## 📸 Demo

### Telegram Workflow (15 segundos)

```
📱 Usuario: [Envía foto del producto]

🤖 Bot: 📸 Foto recibida: Mayonesa Hellmann's
        
        ¿Cuál es la fecha de vencimiento?
        Formatos válidos: DD/MM/AA, DD/MM/YYYY, DD-MM-AA

📱 Usuario: 25/08/26

🤖 Bot: ✅ Producto agregado
        
        📦 Nombre: Mayonesa Hellmann's
        📅 Vencimiento: 25/08/2026
        ⏱ VENCE EN 45 DÍAS
```

> Ver [docs/DEMO.md](docs/DEMO.md) para screenshots completos

## ✨ Características

- **4 sensores nativos** de Home Assistant con datos en tiempo real
- **Servicios** para agregar, modificar y eliminar productos vía automatizaciones
- **Días de advertencia configurables** — personalizá cuándo alertarte (ej: 30, 15, 7, 3, 1 días antes)
- **Soporte de fotos** — URLs de imágenes en atributos de sensores para mostrar en Lovelace
- **Categorización** y ubicación de almacenamiento
- **Códigos de barras** opcionales
- **Importación masiva** desde JSON
- **Instalación via HACS**

> **Nota:** Esta integración provee sensores y servicios. Las alertas se crean mediante automatizaciones de Home Assistant, y las fotos aparecen como URLs en los atributos de sensores para mostrar en tarjetas Lovelace.

## 📦 Instalación

### Via HACS (recomendado)

1. Abrí HACS en Home Assistant
2. Andá a "Integraciones"
3. Hacé clic en ⋮ (menú) → "Repositorios personalizados"
4. Agregá: `https://github.com/diegokelya/ha-product-expiration`
5. Categoría: "Integration"
6. Buscá "Product Expiration Tracker" e instalá
7. **Reiniciá Home Assistant**

### Manual

1. Copiá `custom_components/product_expiration` a `<config>/custom_components/`
2. Reiniciá Home Assistant
3. Andá a **Ajustes** → **Dispositivos y servicios** → **+ Agregar integración**
4. Buscá "Product Expiration Tracker"

## ⚙️ Configuración

1. **Ajustes** → **Dispositivos y servicios** → **+ Agregar integración**
2. Buscá "Product Expiration Tracker"
3. Configurá:
   - **URL base de fotos** (opcional): `http://192.168.1.100:8765` o `/local/product_photos`
   - **Días de advertencia**: `30,15,7,3,1` (separados por comas)

## 📊 Sensores

La integración crea automáticamente:

| Sensor | Descripción |
|--------|-------------|
| `sensor.product_expiration_total_products` | Cantidad total de productos |
| `sensor.product_expiration_expired_products` | Productos ya vencidos |
| `sensor.product_expiration_expiring_soon` | Productos próximos a vencer |
| `sensor.product_expiration_next_expiry` | Nombre del próximo producto a vencer |

Cada sensor incluye **atributos detallados** con lista completa de productos, IDs, fechas, cantidades, categorías e imágenes.

## 🔧 Servicios

### `product_expiration.add_product`

```yaml
service: product_expiration.add_product
data:
  name: "Mayonesa Hellmann's"
  expiry: "2027-02-14"
  image: "mayonesa.jpg"
  quantity: 1
  category: "Condimentos"
  location: "Alacena"
  barcode: "7790895001635"
  confidence: "alta"
```

### `product_expiration.update_product`

```yaml
service: product_expiration.update_product
data:
  product_id: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  quantity: 2
  expiry: "2027-03-01"
```

### `product_expiration.remove_product`

```yaml
service: product_expiration.remove_product
data:
  product_id: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
```

### `product_expiration.import_products`

```yaml
service: product_expiration.import_products
data:
  products:
    - name: "Producto 1"
      expiry: "2027-01-15"
      quantity: 2
    - name: "Producto 2"
      expiry: "2027-02-20"
```

## 🤖 Automatizaciones

### Notificación de productos próximos a vencer

```yaml
automation:
  - alias: "Alertar productos próximos a vencer"
    trigger:
      - platform: state
        entity_id: sensor.product_expiration_expiring_soon
    condition:
      - condition: template
        value_template: "{{ trigger.to_state.state | int > 0 }}"
    action:
      - service: notify.mobile_app_tu_telefono
        data:
          title: "⚠️ Productos por vencer"
          message: >
            Tenés {{ trigger.to_state.state }} producto(s) que vencen pronto:
            {% for product in trigger.to_state.attributes.products %}
            - {{ product.name }} ({{ product.days_until_expiry }} días)
            {% endfor %}
```

### Recordatorio diario

```yaml
automation:
  - alias: "Recordatorio diario de vencimientos"
    trigger:
      - platform: time
        at: "09:00:00"
    condition:
      - condition: template
        value_template: "{{ states('sensor.product_expiration_next_expiry') not in ['unknown', 'unavailable'] }}"
    action:
      - service: notify.telegram
        data:
          message: >
            📅 Próximo vencimiento:
            {{ states('sensor.product_expiration_next_expiry') }}
            ({{ state_attr('sensor.product_expiration_next_expiry', 'days_until_expiry') }} días)
```

## 📸 Workflows de Ingreso de Productos

### Telegram Bot (⚡ Recomendado - 15 segundos)

Workflow ultra-rápido vía Telegram:

1. Enviás foto al bot
2. Respondés con fecha (DD/MM/AA)
3. Producto agregado automáticamente

```bash
cd examples/telegram-workflow
./install.sh
```

Ver [examples/telegram-workflow/README.md](examples/telegram-workflow/README.md) para instrucciones completas.

**Características:**
- ⚡ 15 segundos vs. 2-3 minutos con dashboard
- 📱 Desde cualquier dispositivo móvil
- ✅ Confirmación inmediata con días restantes
- ⚠️ Alerta si el producto ya está vencido

### Simple Upload desde HA Dashboard

Workflow manual con automatizaciones YAML nativas (sin OCR):

```bash
cd examples/simple-upload
```

Ver [examples/simple-upload/README.md](examples/simple-upload/README.md)

**Características:**
- ✅ Sin dependencias externas
- 📸 Snapshot desde cámara de HA
- ⌨️ Ingreso manual de fecha
- 📊 Preview visual antes de confirmar

### Upload con OCR (avanzado)

Workflow completo con extracción automática de fecha:

```bash
cd examples/upload-workflow
./install.sh
```

Ver [examples/upload-workflow/README.md](examples/upload-workflow/README.md)

**Características:**
- 🤖 OCR automático de fecha (pytesseract)
- 📋 Múltiples formatos: DD/MM/YY, VTO: DD/MM/YYYY, DD MES YYYY
- 📸 Snapshot desde cámara o upload manual

## 📤 Migración desde sistema existente

Si tenés un `products.json` previo:

```bash
python3 scripts/import_existing_inventory.py /ruta/a/products.json
```

Genera el YAML para copiarlo en una automatización que importa todo.

O migrá directamente con el script completo:

```bash
python3 scripts/migrate_from_hermes.py
```

## 📋 Dashboard de ejemplo

```yaml
type: vertical-stack
cards:
  - type: entities
    title: Resumen de Vencimientos
    entities:
      - sensor.product_expiration_total_products
      - sensor.product_expiration_expired_products
      - sensor.product_expiration_expiring_soon
      - sensor.product_expiration_next_expiry

  - type: markdown
    title: Productos próximos a vencer
    content: |
      {% set products = state_attr('sensor.product_expiration_expiring_soon', 'products') %}
      {% if products %}
      {% for p in products[:5] %}
      - **{{ p.name }}**: {{ p.status }} ({{ p.expiry }})
      {% endfor %}
      {% else %}
      ✅ No hay productos próximos a vencer
      {% endif %}
```

## 🧪 Desarrollo

```bash
# Clonar
git clone https://github.com/diegokelya/ha-product-expiration
cd ha-product-expiration

# Tests (requiere pytest)
pip3 install -r requirements_test.txt
pytest tests/

# Validar sintaxis
python3 -m py_compile custom_components/product_expiration/*.py
```

## 🤝 Contribuir

1. Fork del proyecto
2. Creá una rama: `git checkout -b feature/nueva-funcionalidad`
3. Commiteá: `git commit -m 'Agrega nueva funcionalidad'`
4. Pusheá: `git push origin feature/nueva-funcionalidad`
5. Abrí un Pull Request

## 📝 Licencia

MIT License - ver [LICENSE](LICENSE)

## 👤 Autor

**Diego Kelyacoubian**

## 🐛 Soporte

[Reportar un problema](https://github.com/diegokelya/ha-product-expiration/issues)

---

**Nota**: Esta integración almacena los datos en `.storage/product_expiration.storage`. Los cambios persisten entre reinicios de Home Assistant.

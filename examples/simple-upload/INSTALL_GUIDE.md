# Instalación paso a paso (vía UI de Home Assistant)

Ya que no tengo acceso directo para crear helpers por API, te doy el código completo para configurar vía File Editor.

## Opción 1: Agregar a configuration.yaml (más rápido)

1. **File Editor** → abrir `/config/configuration.yaml`

2. **Agregar al final** del archivo:

```yaml
# Helpers para upload de fotos de productos
input_text:
  product_name_capture:
    name: Capturar Producto
    icon: mdi:camera
    max: 255
  
  product_name_confirm:
    name: Confirmar Producto
    icon: mdi:check
    max: 255
  
  current_photo_file:
    name: Archivo Foto Actual
    icon: mdi:file-image
    max: 255

input_datetime:
  product_expiry_date:
    name: Fecha Vencimiento Producto
    icon: mdi:calendar
    has_date: true
    has_time: false
```

3. **Guardar** (Ctrl+S o botón Guardar)

4. **Reiniciar HA**: Ajustes → Sistema → Reiniciar

## Opción 2: Via UI (sin editar YAML)

Si preferís crear via interfaz gráfica:

1. Ajustes → Dispositivos y servicios → Helpers → ⊕ CREAR HELPER

2. Repetir 4 veces:

   **Helper 1: Texto**
   - Nombre: `Capturar Producto`
   
   **Helper 2: Texto**
   - Nombre: `Confirmar Producto`
   
   **Helper 3: Texto**
   - Nombre: `Archivo Foto Actual`
   
   **Helper 4: Fecha y/o hora**
   - Nombre: `Fecha Vencimiento Producto`
   - ✅ Fecha
   - ❌ Hora

---

## Siguientes pasos (después de crear helpers)

### 1. Crear carpeta de fotos

File Editor → ícono carpeta → crear:
```
www/product_photos
```

### 2. Crear automatización 1

Ajustes → Automatizaciones → ⊕ → Editar en YAML → pegar:

```yaml
alias: "Producto: Capturar foto"
trigger:
  - platform: state
    entity_id: input_text.product_name_capture
condition:
  - condition: template
    value_template: "{{ trigger.to_state.state | length > 0 }}"
action:
  - service: camera.snapshot
    data:
      entity_id: camera.entrada
      filename: "/config/www/product_photos/{{ now().strftime('%Y%m%d_%H%M%S') }}_{{ states('input_text.product_name_capture') | slugify }}.jpg"
  - service: input_text.set_value
    target:
      entity_id: input_text.current_photo_file
    data:
      value: "{{ now().strftime('%Y%m%d_%H%M%S') }}_{{ states('input_text.product_name_capture') | slugify }}.jpg"
  - service: input_text.set_value
    target:
      entity_id: input_text.product_name_confirm
    data:
      value: "{{ states('input_text.product_name_capture') }}"
  - service: input_text.set_value
    target:
      entity_id: input_text.product_name_capture
    data:
      value: ""
mode: single
```

Guardar.

### 3. Crear automatización 2

Ajustes → Automatizaciones → ⊕ → Editar en YAML → pegar:

```yaml
alias: "Producto: Agregar con foto"
trigger:
  - platform: state
    entity_id: input_datetime.product_expiry_date
condition:
  - condition: template
    value_template: "{{ states('input_text.product_name_confirm') | length > 0 }}"
  - condition: template
    value_template: "{{ states('input_text.current_photo_file') | length > 0 }}"
action:
  - service: product_expiration.add_product
    data:
      name: "{{ states('input_text.product_name_confirm') }}"
      expiry: "{{ states('input_datetime.product_expiry_date') }}"
      image: "{{ states('input_text.current_photo_file') }}"
      confidence: "confirmada por usuario"
  - service: notify.mobile_app_iphone_de_diego
    data:
      title: "✅ Producto agregado"
      message: "{{ states('input_text.product_name_confirm') }} - Vence: {{ states('input_datetime.product_expiry_date') }}"
  - service: input_text.set_value
    target:
      entity_id: input_text.product_name_confirm
    data:
      value: ""
  - service: input_text.set_value
    target:
      entity_id: input_text.current_photo_file
    data:
      value: ""
mode: single
```

Guardar.

### 4. Configurar photo_base_url

Ajustes → Dispositivos y servicios → Product Expiration Tracker → CONFIGURAR:
- `photo_base_url`: `/local/product_photos`

### 5. Probar

Herramientas de desarrollo → Estados → buscar `input_text.product_name_capture` → cambiar valor a "Test Producto"

Debería:
1. Tomar snapshot de camera.entrada
2. Guardar en `/config/www/product_photos/`
3. Llenar `input_text.current_photo_file` con el nombre
4. Llenar `input_text.product_name_confirm` con "Test Producto"

Luego cambiá `input_datetime.product_expiry_date` a una fecha futura → debería agregarse el producto automáticamente.

---

¿Preferís opción 1 (YAML) u opción 2 (UI)?

# Telegram Workflow - Ingreso Rápido de Productos

Workflow ultra-rápido para agregar productos vía Telegram Bot:

1. 📸 Enviás foto del producto al bot
2. ⌨️ Bot pregunta fecha, respondés "DD/MM/AA"
3. ✅ Producto agregado automáticamente con alerta si está vencido

**Tiempo:** ~15 segundos vs. 2-3 minutos con dashboard.

[🇬🇧 English version](README_EN.md)

## Instalación

### 1. Requisitos previos

- Bot de Telegram configurado (token)
- Home Assistant accesible vía HTTP
- Long-Lived Access Token de HA
- Python 3 con `requests` instalado

### 2. Configurar variables de entorno

Editá `~/.hermes/.env` o creá un archivo `.env` local:

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
TELEGRAM_CHAT_ID="406287065"

# Home Assistant
HA_URL="http://homeassistant.local:8123"
HA_TOKEN="tu_long_lived_access_token_aqui"
```

**Obtener HA Token:**
1. Home Assistant → Perfil de usuario → Long-Lived Access Tokens
2. "Create Token" → nombrar "Telegram Product Bot"
3. Copiar el token generado

### 3. Instalar dependencias

```bash
pip3 install requests
# O si usás venv:
uv pip install requests
```

### 4. Hacer ejecutable y probar

```bash
chmod +x telegram_product_bot.py

# Probar manualmente
python3 telegram_product_bot.py
```

Dejá el script corriendo y enviá una foto al bot. Debería responder pidiendo la fecha.

### 5. Ejecutar como servicio (opcional)

**Opción A: Via systemd (Linux)**

Creá `/etc/systemd/system/telegram-product-bot.service`:

```ini
[Unit]
Description=Telegram Product Bot for Home Assistant
After=network.target

[Service]
Type=simple
User=diego
WorkingDirectory=/home/diego/projects/ha-product-expiration/examples/telegram-workflow
EnvironmentFile=/home/diego/.hermes/.env
ExecStart=/usr/bin/python3 /home/diego/projects/ha-product-expiration/examples/telegram-workflow/telegram_product_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Activar:

```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-product-bot
sudo systemctl start telegram-product-bot
sudo systemctl status telegram-product-bot
```

**Opción B: Via Hermes cron job**

```bash
hermes cronjob create \
  --name "telegram-product-bot" \
  --script telegram_product_bot.py \
  --schedule "@reboot" \
  --no-agent
```

**Opción C: Via terminal background en Hermes**

```python
# Desde una sesión de Hermes
terminal(
    command="cd ~/projects/ha-product-expiration/examples/telegram-workflow && python3 telegram_product_bot.py",
    background=True
)
```

## Uso

### Workflow básico

1. **Enviar foto al bot:**
   - Abrí Telegram
   - Andá al chat con tu bot
   - Enviá foto del producto
   - (Opcional) Agregá el nombre del producto como caption

2. **Bot responde:**
   ```
   📸 Foto recibida: Producto
   
   ¿Cuál es la fecha de vencimiento?
   Formatos válidos: DD/MM/AA, DD/MM/YYYY, DD-MM-AA
   ```

3. **Respondés con fecha:**
   ```
   25/08/26
   ```

4. **Bot confirma:**
   ```
   ✅ Producto agregado
   
   📦 Nombre: Mayonesa Hellmann's
   📅 Vencimiento: 25/08/2026
   ⏱ VENCE EN 45 DÍAS
   ```

   O si está vencido:
   ```
   ⚠️ Producto agregado
   
   📦 Nombre: Pan Lactal
   📅 Vencimiento: 15/01/2026
   ⏱ VENCIDO hace 590 días
   ```

### Formatos de fecha aceptados

- `25/08/26` → 2026-08-25
- `25/08/2026` → 2026-08-25
- `25-08-26` → 2026-08-25
- `2026-08-25` → 2026-08-25 (ISO)

### Agregar nombre de producto

**Opción 1:** Caption en la foto (recomendado)

```
[Foto] + "Mayonesa Hellmann's con limón"
```

**Opción 2:** Editar después en HA dashboard

El producto se agrega como "Producto" si no hay caption, podés renombrarlo después.

## Ventajas vs. Dashboard

| Aspecto | Telegram | Dashboard HA |
|---------|----------|--------------|
| Tiempo | ~15 seg | 2-3 min |
| Device | Teléfono móvil | Navegador/app HA |
| Pasos | Foto → Fecha | Abrir HA → Capturar → Campo → Selector → Confirmar |
| UI Navigation | Cero | Múltiple |
| Confirmación | Inmediata con días restantes | Visual en dashboard |
| Alertas | En mismo chat Telegram | Separadas |

## Troubleshooting

### El bot no responde

```bash
# Verificar que el bot esté corriendo
ps aux | grep telegram_product_bot

# Ver logs si está en systemd
sudo journalctl -u telegram-product-bot -f

# Probar manualmente
python3 telegram_product_bot.py
```

### Error "HA_TOKEN not set"

Verificá que el archivo `.env` esté en la ubicación correcta y tenga el formato:

```bash
HA_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

Sin espacios alrededor del `=`.

### Error al agregar producto

- Verificá que Home Assistant esté accesible desde donde corre el bot
- Probá manualmente el servicio:

```bash
curl -X POST http://homeassistant.local:8123/api/services/product_expiration/add_product \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Product",
    "expiry": "2027-01-01",
    "image": "test.jpg"
  }'
```

### La foto no se guarda

El bot guarda fotos en `~/photos/products/`. Verificá permisos:

```bash
mkdir -p ~/photos/products
chmod 755 ~/photos/products
```

## Mejoras futuras

- [ ] OCR automático de fecha (pytesseract)
- [ ] Botones inline para confirmar/editar fecha
- [ ] Categorización automática por nombre
- [ ] Búsqueda de productos existentes
- [ ] Comando `/venc lista` para ver próximos vencimientos
- [ ] Edición/eliminación vía botones inline

## Arquitectura

```
Telegram App
    ↓ [photo + caption]
Telegram Bot (polling)
    ↓ [download photo]
Local Storage (~/photos/products/)
    ↓ [ask date]
User
    ↓ [reply "DD/MM/AA"]
Date Parser
    ↓ [ISO date]
Home Assistant API
    ↓ [product_expiration.add_product]
Product Expiration Storage
    ↓ [update sensors]
Dashboard + Automations
```

## Código

Ver `telegram_product_bot.py` para implementación completa.

Patrón conversacional:
- `load_state()` / `save_state()` para contexto entre mensajes
- `handle_photo_message()` guarda foto y pide fecha
- `handle_text_message()` parsea fecha y llama servicio HA
- `poll_updates()` loop infinito escuchando bot API

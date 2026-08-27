# Product Expiration Tracker - Roadmap de Mejoras

## 🎯 Mejoras Priorizadas

### 🔥 Prioridad ALTA (Impacto inmediato, baja complejidad)

#### 1. **Alertas Inteligentes Telegram** 
**Tiempo estimado:** 30 min  
**Impacto:** Alto — reduce productos desperdiciados

**Implementación:**
```python
# Nuevo script: telegram_alerts.py
# Cron diario 09:00 AM vía Hermes

Funcionalidades:
- Resumen diario: "Tenés 3 productos que vencen esta semana"
- Detalle por urgencia:
  - 🔴 VENCIDO hace X días (2 productos)
  - ⚠️ Vence HOY (1 producto)
  - 🟡 Vence en 3 días (2 productos)
  - 🟢 Vence en 7 días (1 producto)
- Botones inline: [Ver todos] [Marcar consumido]
- Silencio inteligente: no notifica si todo >7 días
```

**Valor:**
- Proactivo vs. reactivo
- Reduce "olvidos"
- Usa canal Telegram ya activo

---

#### 2. **Edición Rápida vía Telegram**
**Tiempo estimado:** 45 min  
**Impacto:** Alto — gestión sin abrir HA

**Comandos:**
```
/venc lista              → Lista próximos 10 vencimientos
/venc consumido <ID>     → Elimina producto
/venc buscar <nombre>    → Busca por nombre
/venc agregar            → Inicia workflow foto
/venc ayuda              → Comandos disponibles
```

**Con botones inline:**
```
📦 Mayonesa Hellmann's
📅 Vence: 25/08/26 (45 días)
🏷️ Condimentos

[✅ Consumido] [➖ -1] [➕ +1] [📝 Editar]
```

**Valor:**
- Cero navegación UI
- Gestión completa desde móvil
- Workflow natural

---

#### 3. **Categorización Automática**
**Tiempo estimado:** 20 min  
**Impacto:** Medio — mejora organización

**Implementación:**
```python
# En telegram_product_bot.py
CATEGORY_MAPPING = {
    "mayonesa|ketchup|mostaza|salsa": "Condimentos",
    "pan|tostadas|galletas|medialunas": "Panificados",
    "leche|yogur|queso|manteca": "Lácteos",
    "pollo|carne|pescado|chorizo": "Carnes",
    "tomate|lechuga|papa|cebolla": "Verduras",
    "manzana|banana|naranja|pera": "Frutas",
    "arroz|fideos|harina|polenta": "Almacén",
}

def auto_categorize(product_name):
    name_lower = product_name.lower()
    for keywords, category in CATEGORY_MAPPING.items():
        if any(kw in name_lower for kw in keywords.split("|")):
            return category
    return "Sin categoría"
```

**Valor:**
- Automático, sin input usuario
- Filtrado por categoría en queries
- Estadísticas por tipo de producto

---

#### 4. **Dashboard Mejorado con Auto-Entities**
**Tiempo estimado:** 1 hora  
**Impacto:** Alto — visualización profesional

**Características:**
- Tarjetas auto-generadas por producto
- Color por urgencia (verde/amarillo/rojo/gris)
- Preview de foto al tap
- Ordenado por días restantes
- Filtros: categoría, ubicación, vencidos

**Dependencias HACS:**
- `auto-entities`
- `button-card`
- `card-mod`

**Ejemplo visual:**
```
┌─────────────────────────────────────┐
│ 🏪 Productos por Vencer             │
├─────────────────────────────────────┤
│ 🔴 VENCIDOS (2)                     │
│  • Pan Lactal - Vencido hace 3 días │
│  • Yogur - Vencido hace 1 día       │
├─────────────────────────────────────┤
│ ⚠️ URGENTE <3 días (1)              │
│  • Queso - Vence en 2 días          │
├─────────────────────────────────────┤
│ 🟡 PRÓXIMOS 3-7 días (3)            │
│  • Mayonesa - 5 días                │
│  • Jamón - 6 días                   │
│  • Leche - 7 días                   │
└─────────────────────────────────────┘
```

**Valor:**
- Vista profesional tipo app comercial
- Acción rápida desde dashboard
- Sin navegación compleja

---

### 🔶 Prioridad MEDIA (Alto impacto, complejidad media)

#### 5. **OCR Automático en Telegram**
**Tiempo estimado:** 1.5 horas  
**Impacto:** Muy alto — workflow 5 segundos

**Implementación:**
```python
# Integrar pytesseract en telegram_product_bot.py

Flow mejorado:
1. Usuario envía foto
2. Bot extrae fecha automáticamente vía OCR
3. Bot pregunta: "Detecté vencimiento: 25/08/26 ¿Correcto?"
4. Usuario: "Sí" o corrige manualmente
5. Producto agregado

Fallback: si OCR falla, pregunta manual (workflow actual)
```

**Consideraciones:**
- Pytesseract ya disponible en workflow upload
- Reusar código de `examples/upload-workflow/ocr_expiry_date.py`
- Agregar dependencia requests + PIL + pytesseract

**Valor:**
- **5 segundos** totales (vs 15 actuales)
- Menos fricción = más uso
- Opcional: fallback a manual si falla

---

#### 6. **Integración con Lista de Compras HA**
**Tiempo estimado:** 1 hora  
**Impacto:** Medio-Alto — cierra el loop

**Funcionalidad:**
```yaml
automation:
  # Cuando producto vence en <7 días, agregar a shopping list
  - alias: "Agregar a compras si por vencer"
    trigger:
      - platform: state
        entity_id: sensor.product_expiration_expiring_soon
    action:
      - repeat:
          for_each: "{{ state_attr('sensor.product_expiration_expiring_soon', 'products') }}"
          sequence:
            - service: shopping_list.add_item
              data:
                name: "{{ repeat.item.name }}"
```

**Mejora Telegram:**
```python
# Botón "Agregar a lista" en notificaciones
callback_data: "add_to_list:product_id"

# Comando
/venc comprar <producto>  → Agrega a shopping_list
```

**Valor:**
- Recordatorio automático de recompra
- Previene "me olvidé de comprar"
- Integración nativa HA

---

#### 7. **Búsqueda por Foto (Visual Search)**
**Tiempo estimado:** 2 horas  
**Impacto:** Medio — "¿qué vencimiento tiene ESTO?"

**Implementación:**
```python
# Usar phash (perceptual hash) para matching

Workflow:
1. Usuario envía foto y escribe: "¿qué es esto?"
2. Bot compara con fotos existentes (phash)
3. Si match >90%: "Encontré: Mayonesa Hellmann's, vence en 45 días"
4. Si no: "No encontrado, ¿querés agregarlo?"

Dependencias:
- imagehash (pip)
- PIL
```

**Casos de uso:**
- "Saqué esto de la heladera, ¿vence pronto?"
- Verificación rápida sin abrir envase

---

#### 8. **Exportar Reportes**
**Tiempo estimado:** 45 min  
**Impacto:** Medio — análisis y auditoría

**Formatos:**
- CSV: productos + fechas + categorías
- PDF: reporte visual con gráficos
- Google Sheets: sync automático vía API

**Comandos Telegram:**
```
/venc reporte          → CSV por Telegram
/venc stats            → Estadísticas: total, vencidos último mes, categoría más común
/venc grafico          → Imagen con timeline de vencimientos
```

**Valor:**
- Análisis de hábitos de consumo
- Identificar productos que no se usan
- Optimización de compras

---

### 🔵 Prioridad BAJA (Mejoras opcionales, alta complejidad)

#### 9. **Reconocimiento de Códigos de Barras**
**Tiempo estimado:** 3 horas  
**Impacto:** Bajo-Medio — automatización avanzada

**Implementación:**
```python
# Integrar pyzbar para barcode reading

Workflow:
1. Usuario envía foto
2. Bot detecta barcode automáticamente
3. Consulta OpenFoodFacts API → nombre producto
4. OCR → fecha vencimiento
5. Bot: "Detecté: Coca-Cola 1.5L, vence 25/08/26 ¿Agregar?"

Base de datos:
- OpenFoodFacts (gratis, open source)
- UPC Database (limitado)
```

**Valor:**
- Nombre exacto sin typing
- Info nutricional extra (bonus)
- Workflow completamente automático

**Desventaja:**
- Productos argentinos poco documentados en DBs internacionales
- Complejidad técnica alta

---

#### 10. **App Mobile Nativa (Flutter/React Native)**
**Tiempo estimado:** 20+ horas  
**Impacto:** Alto — UX premium

**Features:**
- Cámara integrada con preview
- Lista offline-first (sync cuando hay red)
- Notificaciones push nativas
- Widget home screen con próximos vencimientos
- Escaneo barcode nativo

**Consideración:**
- Telegram ya es "la app móvil"
- ROI bajo vs esfuerzo alto
- Mejor: mejorar bot Telegram primero

---

### 🧪 Mejoras de Calidad y DevOps

#### 11. **Testing Automatizado**
**Tiempo estimado:** 2 horas  
**Impacto:** Alto — confiabilidad

```python
# tests/test_telegram_bot.py
def test_date_parser():
    assert parse_date("25/08/26") == "2026-08-25"
    assert parse_date("25-08-2026") == "2026-08-25"
    assert parse_date("invalid") is None

# tests/test_ha_integration.py
async def test_add_product_service(hass):
    await hass.services.async_call(...)
    assert hass.states.get("sensor.product_expiration_total_products").state == "1"
```

**CI/CD:**
```yaml
# .github/workflows/test.yml
- run: pytest tests/ --cov=custom_components/product_expiration
- run: pytest tests/test_telegram_bot.py
```

---

#### 12. **Logs y Monitoreo**
**Tiempo estimado:** 1 hora  
**Impacto:** Medio — debugging y confiabilidad

```python
# Telegram bot: structured logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("/var/log/telegram_product_bot.log"),
        logging.StreamHandler()
    ]
)

# Métricas
- Productos agregados por día
- Errores OCR vs manual
- Tiempo promedio workflow
```

---

#### 13. **Backup Automático**
**Tiempo estimado:** 30 min  
**Impacto:** Alto — protección datos

```bash
# Cron diario vía Hermes
hermes cronjob create \
  --name "backup-products" \
  --schedule "0 3 * * *" \
  --script backup_products.sh

# backup_products.sh
#!/bin/bash
cp ~/.storage/product_expiration.storage \
   ~/backups/products_$(date +%Y%m%d).json
# Retener últimos 30 días
find ~/backups -name "products_*.json" -mtime +30 -delete
```

---

## 🎯 Roadmap Sugerido

### Sprint 1 (1 semana) — Quick Wins
- [x] ✅ Workflow Telegram básico
- [ ] Alertas diarias Telegram
- [ ] Edición rápida vía comandos
- [ ] Categorización automática

### Sprint 2 (2 semanas) — Power Features
- [ ] OCR automático en Telegram
- [ ] Dashboard mejorado con auto-entities
- [ ] Integración shopping list

### Sprint 3 (1 mes) — Advanced
- [ ] Búsqueda visual
- [ ] Reportes y estadísticas
- [ ] Testing automatizado
- [ ] Backup automático

### Backlog (futuro)
- [ ] Reconocimiento barcodes
- [ ] App mobile nativa
- [ ] Multi-usuario con permisos
- [ ] Integración recetas (Home Assistant cookbook)

---

## 🔍 Análisis de Impacto

| Mejora | Tiempo | Impacto UX | Complejidad | ROI |
|--------|--------|------------|-------------|-----|
| Alertas Telegram | 30m | ⭐⭐⭐⭐⭐ | Baja | 🔥🔥🔥🔥🔥 |
| Comandos Telegram | 45m | ⭐⭐⭐⭐⭐ | Media | 🔥🔥🔥🔥🔥 |
| Auto-categorización | 20m | ⭐⭐⭐ | Baja | 🔥🔥🔥🔥 |
| Dashboard mejorado | 1h | ⭐⭐⭐⭐ | Media | 🔥🔥🔥🔥 |
| OCR Telegram | 1.5h | ⭐⭐⭐⭐⭐ | Media | 🔥🔥🔥🔥 |
| Shopping list | 1h | ⭐⭐⭐⭐ | Baja | 🔥🔥🔥 |
| Búsqueda visual | 2h | ⭐⭐⭐ | Alta | 🔥🔥 |
| Reportes | 45m | ⭐⭐⭐ | Baja | 🔥🔥🔥 |
| Barcode scan | 3h | ⭐⭐ | Alta | 🔥 |
| App nativa | 20h+ | ⭐⭐⭐⭐⭐ | Muy Alta | 🔥 |

---

## 💡 Recomendación

**Implementar en orden:**

1. **HOY (30 min):** Alertas Telegram diarias
2. **Esta semana (45 min):** Comandos Telegram básicos
3. **Próxima semana (1.5h):** OCR automático en bot
4. **Mes 1 (2h):** Dashboard mejorado + categorización

**Total invertido:** ~5 horas  
**Mejora en UX:** 10x

Después evaluar: búsqueda visual, reportes, integración shopping list según uso real.

---

## 🎬 ¿Cuál implemento ahora?

Decime cuál querés arrancar y lo desarrollo completo con:
- Código listo para usar
- Docs actualizadas
- Tests (si aplica)
- Commit y push a GitHub

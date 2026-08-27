# Estado de Product Expiration Tracker v1.0.0

**Fecha:** 2026-08-27  
**Estado:** LISTO PARA PRUEBA MANUAL (no producción aún)

## ✅ Completado y Verificado

### Código
- [x] 6 módulos Python compilables sin errores
- [x] Serialización de fechas (date/datetime/str) ✅
- [x] IDs únicos con UUID ✅
- [x] Servicios globales sin duplicados ✅
- [x] photo_base_url funcional ✅
- [x] warn_days configurable ✅
- [x] Estructura hass.data consistente ✅

### Archivos
- [x] manifest.json (domain: product_expiration, v1.0.0)
- [x] strings.json
- [x] translations/es.json
- [x] hacs.json
- [x] services.yaml
- [x] brand/icon.svg
- [x] brand/icon.png (256x256, 952 bytes, PNG válido) ✅

### Infraestructura
- [x] CI/CD workflows (hassfest.yaml, hacs.yaml)
- [x] .gitignore
- [x] Git inicializado con commits
- [x] README.md completo
- [x] LICENSE (MIT)
- [x] CHANGELOG.md

### Scripts
- [x] migrate_from_hermes.py
- [x] import_existing_inventory.py

## ⚠️ Pendiente de Validación

### Tests Unitarios
- [ ] Tests escritos PERO no ejecutados exitosamente
- **Razón:** Requieren `pytest-homeassistant-custom-component` y framework completo de HA
- **Estado actual:** Fallan con `ModuleNotFoundError: No module named 'homeassistant'`
- **Impacto:** NO bloqueante para prueba manual, SÍ para CI/CD automatizado

### Validación en Home Assistant Real
- [ ] Instalación vía UI
- [ ] Agregar productos de prueba
- [ ] Reiniciar y verificar persistencia
- [ ] Probar servicios (add/update/remove/import)
- [ ] Verificar sensores y atributos
- [ ] Options flow (cambiar warn_days, photo_base_url)

### Migración de Inventario Actual
- [ ] **NO TOCAR** hasta validar integración
- [ ] Sistema Hermes actual sigue operativo: `/home/diego/.hermes/data/vencimientos/`
- [ ] Dashboard actual sigue funcionando: `http://homeassistant.local:8123/vencimientos/dashboard`

## 🔧 Configuración Actual de warn_days

**Implementación en `coordinator.py` línea 50-53:**
```python
@property
def expiring_soon_threshold(self) -> int:
    """Get the threshold for 'expiring soon' based on warn_days."""
    # Use the smallest warning day as threshold (typically 1 or 3)
    return min(self.warn_days) if self.warn_days else 7
```

**Semántica:**
- `warn_days` es una lista: `[30, 15, 7, 3, 1]`
- `expiring_soon_threshold` usa el valor **mínimo** (1 día)
- Productos "por vencer" = días hasta vencimiento ≤ threshold
- **Alternativa sugerida:** usar el threshold medio (7 días) en vez del mínimo

**Acción recomendada:** Probar en HA real y ajustar si es necesario.

## 📋 Checklist para Publicar en GitHub

### Antes de crear el repo
- [x] Git init + commits
- [x] Todos los archivos validados
- [x] PNG de branding creado
- [ ] Validación manual en HA de prueba

### Publicación
1. Crear repo: https://github.com/new
   - Nombre: `ha-product-expiration`
   - Público
   - Sin README/LICENSE (ya existen)

2. Push:
   ```bash
   cd /home/diego/projects/ha-product-expiration
   git remote add origin https://github.com/TU_USUARIO/ha-product-expiration.git
   git push -u origin main
   ```

3. Crear release v1.0.0:
   - GitHub → Releases → Draft new release
   - Tag: `v1.0.0`
   - Title: "Product Expiration Tracker v1.0.0"
   - Description: copiar de CHANGELOG.md

4. Configurar:
   - Settings → Topics: `home-assistant`, `hacs`, `python`

### Después de publicar
- [ ] Probar instalación vía HACS en HA de prueba
- [ ] Documentar problemas encontrados
- [ ] Iterar con fixes en v1.0.1 si es necesario

## 🚨 Advertencias

1. **Tests no ejecutados:** Los tests unitarios requieren framework de HA. Validación manual es CRÍTICA.

2. **Migración:** NO ejecutar `migrate_from_hermes.py` hasta validar completamente la integración en HA de prueba.

3. **Sistema actual:** Mantener `/home/diego/.hermes/data/vencimientos/` intacto como backup.

4. **Threshold de warn_days:** La lógica actual usa `min()`, puede ser demasiado estricto. Revisar después de prueba manual.

## 📝 Próximos Pasos

1. **Instalar en HA de prueba** (NO producción):
   ```bash
   sudo cp -r custom_components/product_expiration \
       ~/.homeassistant/custom_components/
   sudo systemctl restart home-assistant
   ```

2. **Agregar via UI:**
   - Settings → Devices & Services → Add Integration
   - Buscar "Product Expiration Tracker"
   - Configurar warn_days y photo_base_url

3. **Probar manualmente:**
   - Agregar producto de prueba
   - Reiniciar HA
   - Verificar persistencia
   - Probar todos los servicios

4. **Solo después:** considerar publicar en GitHub

---

**Conclusión:** La integración está **sintácticamente correcta** y **lista para prueba manual**, pero **NO validada en HA real**. Los tests unitarios fallan por dependencias del framework (esperado). **NO publicar en GitHub hasta validar manualmente en HA de prueba**.

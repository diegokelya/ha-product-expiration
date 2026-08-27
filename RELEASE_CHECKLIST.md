# Release Checklist v1.0.0

## ✅ Bugs críticos corregidos

- [x] Serialización de fechas (date, datetime, string)
- [x] IDs únicos con UUID (no colisiones)
- [x] Servicios registrados globalmente (una sola vez)
- [x] Instancia única de integración (unique_id)
- [x] Manejo robusto de fechas inválidas
- [x] photo_base_url funcional
- [x] warn_days configurable y usado
- [x] Recarga automática al cambiar opciones

## ✅ Archivos validados

- [x] manifest.json
- [x] strings.json
- [x] translations/es.json
- [x] hacs.json
- [x] services.yaml
- [x] brand/icon.svg
- [x] brand/icon.png (o instrucciones para crearlo)
- [x] Sintaxis Python (todos los *.py)

## ✅ Funcionalidades

- [x] 4 sensores nativos
- [x] 4 servicios (add, update, remove, import)
- [x] Config flow con validación
- [x] Options flow
- [x] Almacenamiento persistente
- [x] Atributos completos en sensores
- [x] Soporte de fotos
- [x] Categorías y ubicación
- [x] Códigos de barras

## ✅ Documentación

- [x] README completo y realista
- [x] CHANGELOG.md
- [x] LICENSE (MIT)
- [x] Ejemplo de automatizaciones
- [x] Ejemplo de dashboard
- [x] Scripts de migración
- [x] Instrucciones de instalación HACS

## ✅ Tests

- [x] test_add_product_generates_unique_id
- [x] test_add_product_preserves_existing_id
- [x] test_remove_product
- [x] test_update_product
- [x] test_coordinator_handles_invalid_date
- [x] test_coordinator_uses_warn_days_from_config
- [x] test_coordinator_builds_image_urls
- [x] test_date_normalization
- [x] test_import_products

## ✅ CI/CD

- [x] .github/workflows/hassfest.yaml
- [x] .github/workflows/hacs.yaml
- [x] .gitignore

## 📝 Pre-publicación

- [ ] Convertir icon.svg a icon.png (256x256)
- [ ] Actualizar URLs de GitHub si es necesario
- [ ] Git init + commit inicial
- [ ] Crear repo en GitHub
- [ ] Push a main
- [ ] Crear release v1.0.0 con tag
- [ ] Verificar que HACS detecta el repo

## 🧪 Validación final

- [ ] Copiar a HA de prueba
- [ ] Instalar integración
- [ ] Importar productos actuales
- [ ] Verificar sensores
- [ ] Reiniciar HA
- [ ] Verificar persistencia
- [ ] Probar servicios
- [ ] Probar options flow
- [ ] Validar dashboard de ejemplo

## 🚀 Próximos pasos sugeridos (v1.1+)

- Panel CRUD nativo en Lovelace
- Tarjeta personalizada
- Notificaciones automáticas (integration_quality)
- Soporte de múltiples ubicaciones
- Integración con códigos QR
- Estadísticas históricas

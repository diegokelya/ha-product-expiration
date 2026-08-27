# Publicación en GitHub — Guía Paso a Paso

## Estado Actual

✅ **Código completado y validado**
- Integración Product Expiration Tracker v1.0.0
- Todos los bugs críticos corregidos
- Archivos validados (Python, JSON, PNG)
- Git: rama `main`, 3 commits
- **NO instalado en Home Assistant todavía**

## Prerequisitos

### 1. Cuenta de GitHub
Necesitás una cuenta en https://github.com

### 2. Autenticación Git

**Opción A: Personal Access Token (Recomendado)**

1. Andá a: https://github.com/settings/tokens
2. "Generate new token (classic)"
3. Nombre: `hermes-agent-ha-integration`
4. Scopes necesarios:
   - ✅ `repo` (acceso completo a repositorios)
   - ✅ `workflow` (para GitHub Actions)
5. Expiration: 90 días
6. "Generate token"
7. **Copiá el token** (no se vuelve a mostrar)

8. Configurá git para usar el token:
   ```bash
   git config --global credential.helper store
   ```

**Opción B: SSH Key**

Si preferís SSH:
```bash
ssh-keygen -t ed25519 -C "tu-email@example.com"
cat ~/.ssh/id_ed25519.pub
# Agregar la clave pública en: https://github.com/settings/keys
```

### 3. Verificar Git Identity

```bash
git config --global user.name
git config --global user.email
```

Si están vacíos:
```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu-email@example.com"
```

## Publicación — Método Interactivo

### Ejecutar el Script

```bash
cd /home/diego/projects/ha-product-expiration
./publish_to_github.sh
```

El script te guiará paso a paso:
1. Verificación pre-publicación
2. Te pide tu usuario de GitHub
3. Te dice cómo crear el repo en GitHub
4. Conecta el remote
5. Pushea el código
6. Crea y pushea el tag v1.0.0
7. Te da instrucciones para el release manual

### Cuando te pida credenciales

**Usuario:** tu-usuario-github  
**Password:** pega el **Personal Access Token** (NO tu contraseña de GitHub)

Git guardará las credenciales y no las volverá a pedir.

## Publicación — Método Manual

### 1. Crear repositorio en GitHub

1. Andá a: https://github.com/new
2. Configuración:
   - **Repository name:** `ha-product-expiration`
   - **Description:** `Home Assistant integration for product expiration tracking`
   - **Public** ✅
   - **NO agregar README** ❌
   - **NO agregar .gitignore** ❌
   - **NO agregar license** ❌
3. "Create repository"

### 2. Conectar y pushear

```bash
cd /home/diego/projects/ha-product-expiration

# Agregar remote (reemplazá TU-USUARIO)
git remote add origin https://github.com/TU-USUARIO/ha-product-expiration.git

# Push
git push -u origin main

# Crear y pushear tag
git tag -a v1.0.0 -m "Product Expiration Tracker v1.0.0"
git push origin v1.0.0
```

### 3. Crear Release en GitHub

1. Andá a: `https://github.com/TU-USUARIO/ha-product-expiration/releases/new`
2. Configuración:
   - **Choose a tag:** v1.0.0
   - **Release title:** `Product Expiration Tracker v1.0.0`
   - **Description:** copiá el contenido de `CHANGELOG.md`
   - ✅ **Set as the latest release**
3. "Publish release"

### 4. Configurar Topics

1. En la página principal del repo
2. Click en ⚙️ junto a "About"
3. Agregá topics:
   - `home-assistant`
   - `hacs`
   - `python`
   - `expiration-tracker`

## Verificación Post-Publicación

### Checks en GitHub

- [ ] Código visible en: `https://github.com/TU-USUARIO/ha-product-expiration`
- [ ] Tag v1.0.0 existe en: `.../tags`
- [ ] Release v1.0.0 existe en: `.../releases`
- [ ] Topics configurados
- [ ] GitHub Actions ejecutándose (`.../actions`)

### Workflows Esperados

Deberías ver 2 workflows ejecutándose automáticamente:
1. **HACS Validation** — valida `hacs.json`
2. **Hassfest** — valida `manifest.json`

Si alguno falla, revisá los logs en la pestaña "Actions".

## Instalación vía HACS

Los usuarios (incluyendo vos para probar) podrán instalar así:

1. **HACS** → **Integraciones**
2. **⋮** (menú) → **Repositorios personalizados**
3. **URL:** `https://github.com/TU-USUARIO/ha-product-expiration`
4. **Categoría:** Integration
5. **Agregar**
6. Buscar "Product Expiration Tracker"
7. **Descargar**
8. **Reiniciar Home Assistant**
9. **Settings** → **Devices & Services** → **Add Integration** → "Product Expiration Tracker"

## ⚠️ IMPORTANTE: Validación Obligatoria

**ANTES de migrar tu inventario real:**

1. Instalá en HA de **PRUEBA** (no producción)
2. Agregá 2-3 productos de prueba
3. Reiniciá HA
4. Verificá que los productos persisten
5. Probá los 4 servicios (add, update, remove, import)
6. Verificá los 4 sensores
7. Probá cambiar `warn_days` via Options

**Solo después:** ejecutar `scripts/migrate_from_hermes.py`

Tu sistema actual sigue funcionando:
```
/home/diego/.hermes/data/vencimientos/products.json
http://homeassistant.local:8123/vencimientos/dashboard
```

## Troubleshooting

### "Authentication failed"

**Causa:** Usaste tu contraseña de GitHub en vez del token.

**Solución:**
```bash
# Borrar credenciales guardadas
git credential reject << EOF
protocol=https
host=github.com
EOF

# Reintentar push (te volverá a pedir credenciales)
git push -u origin main
# Username: tu-usuario
# Password: [pegá el Personal Access Token]
```

### "remote: Permission denied"

**Causa:** El token no tiene scope `repo`.

**Solución:** Crear un nuevo token con el scope correcto.

### "fatal: remote origin already exists"

**Solución:**
```bash
git remote remove origin
git remote add origin https://github.com/TU-USUARIO/ha-product-expiration.git
```

### GitHub Actions fallan

**HACS o Hassfest con errores:**
1. Andá a la pestaña "Actions"
2. Click en el workflow que falló
3. Click en el job
4. Revisá los logs
5. Corregí el archivo indicado
6. Commit y push

## Próximos Pasos

Después de publicar y validar:

1. **Compartir:**
   - Link: `https://github.com/TU-USUARIO/ha-product-expiration`
   - Reddit: r/homeassistant
   - Comunidad de HA Argentina

2. **Mantenimiento:**
   - Issues para bugs
   - Pull requests para mejoras
   - Releases con versionado semántico (v1.0.1, v1.1.0, etc.)

3. **Mejoras Futuras (v1.1+):**
   - Panel Lovelace nativo
   - Tarjeta personalizada
   - Notificaciones automáticas
   - App móvil para escanear códigos de barras
   - Integración con listas de compras

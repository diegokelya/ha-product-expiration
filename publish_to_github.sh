#!/bin/bash
# Publicar Product Expiration Tracker v1.0.0 en GitHub
# EJECUTAR DESPUÉS DE CREAR EL REPO EN https://github.com/new

set -e

cd "$(dirname "$0")"

echo "════════════════════════════════════════════════════════════════"
echo "  PUBLICAR HA PRODUCT EXPIRATION TRACKER v1.0.0 EN GITHUB"
echo "════════════════════════════════════════════════════════════════"
echo

# Verificar que estamos en la rama main
BRANCH=$(git branch --show-current)
if [ "$BRANCH" != "main" ]; then
    echo "❌ ERROR: Estás en la rama '$BRANCH', debe ser 'main'"
    exit 1
fi

# Verificar que no hay cambios sin commitear
if ! git diff-index --quiet HEAD --; then
    echo "❌ ERROR: Hay cambios sin commitear"
    echo "   Ejecutá: git status"
    exit 1
fi

echo "✅ Rama: main"
echo "✅ Working tree limpio"
echo

# Solicitar nombre de usuario de GitHub
read -p "Ingresá tu usuario de GitHub: " GH_USER
if [ -z "$GH_USER" ]; then
    echo "❌ ERROR: Usuario vacío"
    exit 1
fi

echo
echo "════════════════════════════════════════════════════════════════"
echo "  PASO 1: Crear el repositorio en GitHub"
echo "════════════════════════════════════════════════════════════════"
echo
echo "Abrí tu navegador en:"
echo "  https://github.com/new"
echo
echo "Configuración:"
echo "  - Owner: $GH_USER"
echo "  - Repository name: ha-product-expiration"
echo "  - Description: Home Assistant integration for product expiration tracking"
echo "  - Public"
echo "  - ❌ NO agregar README"
echo "  - ❌ NO agregar .gitignore"
echo "  - ❌ NO agregar license"
echo
read -p "Presioná ENTER cuando hayas creado el repositorio..."

# Agregar remote
echo
echo "════════════════════════════════════════════════════════════════"
echo "  PASO 2: Conectar con GitHub"
echo "════════════════════════════════════════════════════════════════"
echo

if git remote | grep -q '^origin$'; then
    echo "⚠️  Remote 'origin' ya existe, eliminando..."
    git remote remove origin
fi

REPO_URL="https://github.com/$GH_USER/ha-product-expiration.git"
git remote add origin "$REPO_URL"
echo "✅ Remote agregado: $REPO_URL"

# Push
echo
echo "════════════════════════════════════════════════════════════════"
echo "  PASO 3: Push a GitHub"
echo "════════════════════════════════════════════════════════════════"
echo

echo "Pusheando código..."
if git push -u origin main; then
    echo "✅ Push exitoso"
else
    echo "❌ ERROR en push"
    echo
    echo "Si te pide usuario/password:"
    echo "  - Usuario: $GH_USER"
    echo "  - Password: usa un Personal Access Token (NO tu contraseña)"
    echo
    echo "Para crear un token:"
    echo "  1. Andá a: https://github.com/settings/tokens"
    echo "  2. Generate new token (classic)"
    echo "  3. Scopes: repo, workflow"
    echo "  4. Copiá el token y usalo como password"
    echo
    exit 1
fi

# Crear tag
echo
echo "════════════════════════════════════════════════════════════════"
echo "  PASO 4: Crear tag v1.0.0"
echo "════════════════════════════════════════════════════════════════"
echo

git tag -a v1.0.0 -m "Product Expiration Tracker v1.0.0

Initial release:
- Track products with expiration dates
- 4 native sensors (total, expired, expiring soon, next)
- Services: add, update, remove, import
- Config flow with warn_days and photo_base_url
- HACS compatible
- Spanish/English translations"

git push origin v1.0.0
echo "✅ Tag v1.0.0 creado y pusheado"

# Instrucciones finales
echo
echo "════════════════════════════════════════════════════════════════"
echo "  ✅ PUBLICACIÓN COMPLETA"
echo "════════════════════════════════════════════════════════════════"
echo
echo "Repositorio: https://github.com/$GH_USER/ha-product-expiration"
echo
echo "════════════════════════════════════════════════════════════════"
echo "  PASO 5: Crear Release en GitHub (MANUAL)"
echo "════════════════════════════════════════════════════════════════"
echo
echo "1. Andá a: https://github.com/$GH_USER/ha-product-expiration/releases/new"
echo
echo "2. Configurá el release:"
echo "   - Tag: v1.0.0 (seleccionar del dropdown)"
echo "   - Release title: Product Expiration Tracker v1.0.0"
echo "   - Description: (copiá desde CHANGELOG.md)"
echo "   - ✅ Set as the latest release"
echo "   - Publish release"
echo
echo "════════════════════════════════════════════════════════════════"
echo "  PASO 6: Configurar Topics"
echo "════════════════════════════════════════════════════════════════"
echo
echo "1. Andá a: https://github.com/$GH_USER/ha-product-expiration"
echo "2. Click en ⚙️ Settings (rueda dentada al lado de About)"
echo "3. Agregá topics: home-assistant, hacs, python"
echo
echo "════════════════════════════════════════════════════════════════"
echo "  INSTALACIÓN VIA HACS"
echo "════════════════════════════════════════════════════════════════"
echo
echo "Los usuarios podrán instalarlo así:"
echo
echo "1. HACS → Integraciones"
echo "2. ⋮ (menú) → Repositorios personalizados"
echo "3. URL: https://github.com/$GH_USER/ha-product-expiration"
echo "4. Categoría: Integration"
echo "5. Buscar 'Product Expiration Tracker' e instalar"
echo
echo "════════════════════════════════════════════════════════════════"
echo "  ⚠️  VALIDACIÓN PENDIENTE"
echo "════════════════════════════════════════════════════════════════"
echo
echo "ANTES de recomendar a otros usuarios:"
echo
echo "1. Instalar en TU Home Assistant de PRUEBA"
echo "2. Agregar 2-3 productos de prueba"
echo "3. Reiniciar HA y verificar persistencia"
echo "4. Probar todos los servicios"
echo "5. Solo después: migrar inventario real"
echo
echo "Ver instrucciones en: STATUS.md"
echo
echo "════════════════════════════════════════════════════════════════"

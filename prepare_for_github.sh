#!/bin/bash
set -euo pipefail

echo "🚀 Preparando repositorio para GitHub..."

cd /home/diego/projects/ha-product-expiration

# Inicializar git si no existe
if [ ! -d .git ]; then
    git init
    echo "✓ Repositorio git inicializado"
fi

# Agregar todos los archivos
git add .

# Verificar sintaxis Python
echo "🔍 Validando sintaxis Python..."
find custom_components/product_expiration -name "*.py" -exec python3 -m py_compile {} \;
echo "✓ Sintaxis Python válida"

# Verificar JSON
echo "🔍 Validando archivos JSON..."
find . -name "*.json" -exec python3 -m json.tool {} \; >/dev/null
echo "✓ JSON válido"

# Crear commit inicial
if ! git log -1 >/dev/null 2>&1; then
    git config user.email "diego@example.com" || true
    git config user.name "Diego Kelyacoubian" || true
    git commit -m "Initial commit: Home Assistant Product Expiration Tracker v1.0.0

- Full integration with config flow
- Four sensors (total, expired, expiring soon, next expiry)
- Services for CRUD operations
- Photo support
- HACS compatible
- Spanish translations
- Migration scripts from existing system"
    echo "✓ Commit inicial creado"
fi

echo ""
echo "✅ Repositorio listo para GitHub"
echo ""
echo "Próximos pasos:"
echo "1. Creá el repo en GitHub: https://github.com/new"
echo "   Nombre sugerido: ha-product-expiration"
echo ""
echo "2. Ejecutá:"
echo "   cd /home/diego/projects/ha-product-expiration"
echo "   git remote add origin https://github.com/TU_USUARIO/ha-product-expiration.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Configurá el repo en GitHub:"
echo "   - Settings → Topics: home-assistant, hacs, expiration-tracker, python"
echo "   - Creá un release v1.0.0 con tag para que HACS lo detecte"
echo ""
echo "4. Para instalar en tu HA:"
echo "   - Copiá la carpeta custom_components/product_expiration a tu config/custom_components/"
echo "   - O agregá el repo en HACS como repositorio personalizado"

#!/bin/bash
set -e

echo "=== Telegram Product Bot - Instalación ==="
echo

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "❌ Python 3 no encontrado. Instalá Python 3 primero."
    exit 1
fi

echo "✅ Python 3 encontrado: $(python3 --version)"

# Install dependencies
echo
echo "Instalando dependencias..."
pip3 install requests --quiet || {
    echo "⚠️  pip3 install falló, intentando con --user"
    pip3 install --user requests --quiet
}

echo "✅ Dependencias instaladas"

# Create photos directory
PHOTOS_DIR="$HOME/photos/products"
mkdir -p "$PHOTOS_DIR"
echo "✅ Directorio de fotos creado: $PHOTOS_DIR"

# Create state directory
STATE_DIR="$HOME/.hermes/data"
mkdir -p "$STATE_DIR"
echo "✅ Directorio de estado creado: $STATE_DIR"

# Make script executable
chmod +x telegram_product_bot.py
echo "✅ Script marcado como ejecutable"

# Check for .env file
ENV_FILE="$HOME/.hermes/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo
    echo "⚠️  No se encontró archivo .env en $ENV_FILE"
    echo
    echo "Creando plantilla..."
    mkdir -p "$(dirname "$ENV_FILE")"
    cat > "$ENV_FILE" << 'EOF'
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN_HERE"
TELEGRAM_CHAT_ID="406287065"

# Home Assistant Configuration
HA_URL="http://homeassistant.local:8123"
HA_TOKEN="YOUR_HA_LONG_LIVED_TOKEN_HERE"
EOF
    echo "✅ Plantilla creada en $ENV_FILE"
    echo
    echo "❗ ACCIÓN REQUERIDA:"
    echo "   1. Editá $ENV_FILE"
    echo "   2. Reemplazá YOUR_BOT_TOKEN_HERE con tu token de Telegram"
    echo "   3. Reemplazá YOUR_HA_LONG_LIVED_TOKEN_HERE con tu token de HA"
    echo
    echo "Para obtener HA token:"
    echo "   - HA → Perfil → Long-Lived Access Tokens → Create Token"
    echo
else
    echo "✅ Archivo .env encontrado: $ENV_FILE"
    
    # Check if tokens are set
    if grep -q "YOUR_BOT_TOKEN_HERE" "$ENV_FILE" || grep -q "YOUR_HA_LONG_LIVED_TOKEN_HERE" "$ENV_FILE"; then
        echo
        echo "⚠️  Tokens no configurados en .env"
        echo "   Editá $ENV_FILE y reemplazá los placeholders"
    else
        echo "✅ Tokens configurados"
    fi
fi

echo
echo "=== Instalación completa ==="
echo
echo "Para probar el bot:"
echo "  source $ENV_FILE"
echo "  python3 telegram_product_bot.py"
echo
echo "Para ejecutar como servicio, ver README.md sección 5"
echo

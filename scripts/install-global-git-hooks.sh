#!/bin/bash

# Script para instalar los git hooks de forma global en el sistema

# Colores para mensajes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Función para mostrar mensajes de error y salir
error_exit() {
    echo -e "${RED}❌ ERROR: $1${NC}"
    exit 1
}

# Función para mostrar mensajes de advertencia
warning() {
    echo -e "${YELLOW}⚠️ ADVERTENCIA: $1${NC}"
}

# Función para mostrar mensajes de éxito
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

echo "🔧 Instalando git hooks de forma global..."

# Verificar que los scripts de git hooks existen
if [ ! -f "scripts/git-hooks/pre-commit" ] || [ ! -f "scripts/git-hooks/pre-push" ]; then
    error_exit "No se encontraron los scripts de git hooks en scripts/git-hooks/. Por favor, verifica que los archivos existen."
fi

# Crear el directorio ~/.git-hooks si no existe
mkdir -p ~/.git-hooks

# Crear el script pre-commit simplificado
cat > ~/.git-hooks/pre-commit << 'EOF'
#!/bin/bash

# Script de pre-commit simplificado para validar el código
echo "🔍 Ejecutando validaciones pre-commit simplificadas..."

# Colores para mensajes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Función para mostrar mensajes de error y salir
error_exit() {
    echo -e "${RED}❌ ERROR: $1${NC}"
    exit 1
}

# Función para mostrar mensajes de éxito
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Verificar que no haya claves API expuestas en el código
echo "🔑 Verificando que no haya claves API expuestas en el código..."

# Obtener los archivos que se van a commitear (excluyendo .env y secrets.toml)
FILES_TO_CHECK=$(git diff --cached --name-only --diff-filter=ACM | grep -v -E "\.env$|secrets\.toml$" || true)

if [ -z "$FILES_TO_CHECK" ]; then
    success "No hay archivos para verificar."
    exit 0
fi

# Buscar patrones de claves API solo en los archivos que se van a commitear
for FILE in $FILES_TO_CHECK; do
    # Verificar si el archivo existe
    if [ ! -f "$FILE" ]; then
        continue
    fi

    # Buscar patrones de OpenAI API key
    if grep -q "sk-[0-9a-zA-Z]\{48\}" "$FILE" 2>/dev/null; then
        error_exit "Se encontró una posible clave API de OpenAI en $FILE"
    fi

    # Buscar patrones de Mistral API key
    if grep -q "r[0-9a-zA-Z]\{32\}" "$FILE" 2>/dev/null; then
        error_exit "Se encontró una posible clave API de Mistral en $FILE"
    fi

    # Buscar patrones de OpenRouter API key
    if grep -q "sk-or-v1-[0-9a-zA-Z]\{64\}" "$FILE" 2>/dev/null; then
        error_exit "Se encontró una posible clave API de OpenRouter en $FILE"
    fi

    # Buscar patrones de Google API key
    if grep -q "AIza[0-9a-zA-Z_-]\{35\}" "$FILE" 2>/dev/null; then
        error_exit "Se encontró una posible clave API de Google en $FILE"
    fi

    # Buscar patrones de Tavily API key
    if grep -q "tvly-[0-9a-zA-Z]\{32\}" "$FILE" 2>/dev/null; then
        error_exit "Se encontró una posible clave API de Tavily en $FILE"
    fi
done

success "No se encontraron claves API expuestas en el código."

# Verificar que no haya archivos grandes (>10MB)
echo "📦 Verificando que no haya archivos grandes..."

for FILE in $FILES_TO_CHECK; do
    if [ -f "$FILE" ]; then
        SIZE=$(du -k "$FILE" 2>/dev/null | cut -f1)
        if [ ! -z "$SIZE" ] && [ "$SIZE" -gt 10240 ]; then
            error_exit "El archivo $FILE es demasiado grande (${SIZE}KB). Considera usar .gitignore para excluir archivos grandes."
        fi
    fi
done

success "No se encontraron archivos grandes."

# Verificar que no haya conflictos de merge sin resolver
echo "🔄 Verificando que no haya conflictos de merge sin resolver..."

for FILE in $FILES_TO_CHECK; do
    if [ -f "$FILE" ] && grep -q -E "^[<>=]{7}" "$FILE" 2>/dev/null; then
        error_exit "Se encontraron conflictos de merge sin resolver en $FILE. Por favor, resuelve los conflictos antes de commitear."
    fi
done

success "No se encontraron conflictos de merge sin resolver."

# Todas las validaciones pasaron
echo -e "${GREEN}✅ Todas las validaciones pre-commit pasaron exitosamente.${NC}"
exit 0
EOF

# Copiar el script pre-push
cp scripts/git-hooks/pre-push ~/.git-hooks/

# Hacer los scripts ejecutables
chmod +x ~/.git-hooks/pre-commit
chmod +x ~/.git-hooks/pre-push

# Configurar Git para usar la ubicación permanente
git config --global core.hooksPath ~/.git-hooks

success "Git hooks instalados globalmente en ~/.git-hooks"
echo "Los siguientes hooks están activos para todos los repositorios Git:"
echo "  - pre-commit: Se ejecuta antes de cada commit para validar el código"
echo "  - pre-push: Se ejecuta antes de cada push para validar el código"
echo ""
echo "Para desactivar temporalmente un hook, usa git con la opción --no-verify:"
echo "  git commit --no-verify"
echo "  git push --no-verify"
echo ""
echo "Para volver a la configuración por defecto de git hooks, ejecuta:"
echo "  git config --global --unset core.hooksPath"

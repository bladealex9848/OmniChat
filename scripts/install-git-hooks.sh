#!/bin/bash

# Script para instalar los git hooks en el repositorio actual

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

echo "🔧 Instalando git hooks para OmniChat..."

# Verificar que estamos en un repositorio git
if [ ! -d ".git" ]; then
    error_exit "No se encontró un repositorio git en el directorio actual. Por favor, ejecuta este script desde la raíz del repositorio."
fi

# Verificar que los scripts de git hooks existen
if [ ! -f "scripts/git-hooks/pre-commit" ] || [ ! -f "scripts/git-hooks/pre-push" ]; then
    error_exit "No se encontraron los scripts de git hooks en scripts/git-hooks/. Por favor, verifica que los archivos existen."
fi

# Crear el directorio .git/hooks si no existe
mkdir -p .git/hooks

# Copiar los scripts de git hooks
cp scripts/git-hooks/pre-commit .git/hooks/
cp scripts/git-hooks/pre-push .git/hooks/

# Hacer los scripts ejecutables
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/pre-push

success "Git hooks instalados correctamente."
echo "Los siguientes hooks están activos:"
echo "  - pre-commit: Se ejecuta antes de cada commit para validar el código"
echo "  - pre-push: Se ejecuta antes de cada push para validar el código"
echo ""
echo "Para desactivar temporalmente un hook, usa git con la opción --no-verify:"
echo "  git commit --no-verify"
echo "  git push --no-verify"
echo ""
echo "Para desinstalar los hooks, elimina los archivos de .git/hooks/:"
echo "  rm .git/hooks/pre-commit"
echo "  rm .git/hooks/pre-push"
echo ""
echo "Para instalar estos hooks globalmente para todos tus repositorios, ejecuta:"
echo "  git config --global core.hooksPath \$PWD/scripts/git-hooks"
echo ""
echo "Para volver a la configuración por defecto de git hooks, ejecuta:"
echo "  git config --global --unset core.hooksPath"

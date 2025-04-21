# Scripts de Utilidad para OmniChat

Este directorio contiene scripts de utilidad para el proyecto OmniChat.

## Git Hooks

Los git hooks son scripts que se ejecutan automáticamente en ciertos momentos del flujo de trabajo de git, como antes de un commit (pre-commit) o antes de un push (pre-push).

### Hooks Disponibles

- **pre-commit**: Se ejecuta antes de cada commit para validar el código.
  - Verifica que no haya claves API expuestas en el código
  - Verifica que no haya print statements en el código Python
  - Verifica que no haya archivos grandes (>10MB)
  - Verifica que no haya conflictos de merge sin resolver
  - Verifica que los archivos Python tengan el formato correcto (si black está instalado)
  - Verifica que los archivos Python no tengan errores de sintaxis
  - Verifica que los archivos de texto no tengan espacios en blanco al final de las líneas

- **pre-push**: Se ejecuta antes de cada push para validar el código.
  - Verifica que todos los tests pasen (si pytest está instalado)
  - Verifica que no haya claves API expuestas en el código
  - Verifica que requirements.txt esté actualizado
  - Verifica que README.md esté actualizado

### Instalación

Para instalar los git hooks en el repositorio actual, ejecuta:

```bash
./scripts/install-git-hooks.sh
```

### Instalación Global

Para instalar estos hooks globalmente para todos tus repositorios (actual y futuros), ejecuta:

```bash
./scripts/install-global-git-hooks.sh
```

Esto copiará los scripts a `~/.git-hooks/` y configurará Git para usar esa ubicación permanente.

Alternativamente, puedes hacer la instalación global manualmente:

```bash
# Crear el directorio para los hooks globales
mkdir -p ~/.git-hooks

# Copiar los scripts
cp scripts/git-hooks/* ~/.git-hooks/

# Hacer los scripts ejecutables
chmod +x ~/.git-hooks/*

# Configurar Git para usar la ubicación permanente
git config --global core.hooksPath ~/.git-hooks
```

Para volver a la configuración por defecto de git hooks, ejecuta:

```bash
git config --global --unset core.hooksPath
```

### Desactivación Temporal

Para desactivar temporalmente un hook, usa git con la opción `--no-verify`:

```bash
git commit --no-verify
git push --no-verify
```

### Desinstalación

Para desinstalar los hooks, elimina los archivos de `.git/hooks/`:

```bash
rm .git/hooks/pre-commit
rm .git/hooks/pre-push
```

"""
Script para limpiar la caché de Python y reiniciar la aplicación.
"""

import os
import sys
import importlib
import shutil

def clean_cache():
    """Limpia la caché de Python."""
    # Eliminar archivos .pyc
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))
                print(f"Eliminado: {os.path.join(root, file)}")
        
        # Eliminar directorios __pycache__
        for dir in dirs:
            if dir == '__pycache__':
                shutil.rmtree(os.path.join(root, dir))
                print(f"Eliminado directorio: {os.path.join(root, dir)}")
    
    # Recargar módulos
    for module in list(sys.modules.keys()):
        if module.startswith('utils') or module == 'sidebar_info':
            if module in sys.modules:
                importlib.reload(sys.modules[module])
                print(f"Recargado módulo: {module}")

if __name__ == "__main__":
    clean_cache()
    print("Caché limpiada correctamente.")

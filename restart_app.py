"""
Script para reiniciar la aplicación Streamlit y limpiar la caché.
"""

import os
import sys
import importlib
import shutil
import subprocess
import time

def clean_cache():
    """Limpia la caché de Python."""
    print("Limpiando caché de Python...")
    
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

def restart_app():
    """Reinicia la aplicación Streamlit."""
    print("Reiniciando aplicación Streamlit...")
    
    # Detener cualquier proceso de Streamlit en ejecución
    try:
        subprocess.run(["pkill", "-f", "streamlit"], check=False)
        time.sleep(1)  # Esperar a que se detengan los procesos
    except Exception as e:
        print(f"Error al detener procesos de Streamlit: {e}")
    
    # Iniciar la aplicación Streamlit
    try:
        subprocess.Popen(["streamlit", "run", "Inicio.py"])
        print("Aplicación Streamlit iniciada correctamente.")
    except Exception as e:
        print(f"Error al iniciar la aplicación Streamlit: {e}")

if __name__ == "__main__":
    clean_cache()
    restart_app()
    print("Proceso completado. La aplicación debería estar ejecutándose en http://localhost:8501")

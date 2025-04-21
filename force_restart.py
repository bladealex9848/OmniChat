"""
Script para forzar el reinicio de la aplicación Streamlit y limpiar la caché de Python.
Este script es más agresivo que restart_app.py y garantiza que todos los módulos se recarguen.
"""

import os
import sys
import shutil
import subprocess
import time

def clean_cache_aggressively():
    """Limpia la caché de Python de manera agresiva."""
    print("Limpiando caché de Python de manera agresiva...")
    
    # Eliminar archivos .pyc
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                try:
                    os.remove(os.path.join(root, file))
                    print(f"Eliminado: {os.path.join(root, file)}")
                except Exception as e:
                    print(f"Error al eliminar {os.path.join(root, file)}: {e}")
        
        # Eliminar directorios __pycache__
        for dir in dirs:
            if dir == '__pycache__':
                try:
                    shutil.rmtree(os.path.join(root, dir))
                    print(f"Eliminado directorio: {os.path.join(root, dir)}")
                except Exception as e:
                    print(f"Error al eliminar directorio {os.path.join(root, dir)}: {e}")

def kill_streamlit_processes():
    """Mata todos los procesos de Streamlit."""
    print("Matando todos los procesos de Streamlit...")
    try:
        # En macOS/Linux
        subprocess.run(["pkill", "-f", "streamlit"], check=False)
        time.sleep(2)  # Esperar a que se detengan los procesos
    except Exception as e:
        print(f"Error al matar procesos de Streamlit: {e}")

def clear_streamlit_cache():
    """Limpia la caché de Streamlit."""
    print("Limpiando caché de Streamlit...")
    cache_dir = os.path.expanduser("~/.streamlit/cache")
    if os.path.exists(cache_dir):
        try:
            shutil.rmtree(cache_dir)
            print(f"Caché de Streamlit eliminada: {cache_dir}")
        except Exception as e:
            print(f"Error al eliminar caché de Streamlit: {e}")

def start_streamlit():
    """Inicia la aplicación Streamlit."""
    print("Iniciando aplicación Streamlit...")
    try:
        # Usar subprocess.Popen para no bloquear este script
        process = subprocess.Popen(
            ["streamlit", "run", "Inicio.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Esperar un poco para ver si hay errores inmediatos
        time.sleep(3)
        
        # Verificar si el proceso sigue vivo
        if process.poll() is None:
            print("Aplicación Streamlit iniciada correctamente.")
        else:
            stdout, stderr = process.communicate()
            print(f"Error al iniciar Streamlit: {stderr}")
    except Exception as e:
        print(f"Error al iniciar la aplicación Streamlit: {e}")

if __name__ == "__main__":
    # Ejecutar todas las funciones de limpieza y reinicio
    clean_cache_aggressively()
    kill_streamlit_processes()
    clear_streamlit_cache()
    start_streamlit()
    
    print("\nProceso completado. La aplicación debería estar ejecutándose en http://localhost:8501")
    print("Si la aplicación no se inicia correctamente, intenta ejecutar manualmente:")
    print("cd /Volumes/NVMe1TB/GitHub/OmniChat && source venv/bin/activate && streamlit run Inicio.py")

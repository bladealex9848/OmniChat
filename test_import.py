import sys
import os

# Añadir el directorio raíz al path para poder importar utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import utils

# Verificar qué tipo de objeto es utils
print(f"Tipo de utils: {type(utils)}")

# Verificar si utils tiene el atributo enable_chat_history
print(f"¿utils tiene enable_chat_history? {hasattr(utils, 'enable_chat_history')}")

# Verificar qué atributos tiene utils
print(f"Atributos de utils: {dir(utils)}")

# Intentar usar la función enable_chat_history
if hasattr(utils, 'enable_chat_history'):
    print("La función enable_chat_history está disponible")

    # Definir una función de prueba
    @utils.enable_chat_history
    def test_function():
        print("Esta es una función de prueba")

    print("Función decorada creada correctamente")
else:
    print("La función enable_chat_history NO está disponible")

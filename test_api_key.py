# Este es un archivo de prueba para verificar el funcionamiento del pre-commit hook

# Esta línea debería ser detectada por el pre-commit hook como una clave API expuesta
api_key = "sk-1234567890abcdef1234567890abcdef1234567890abcdef1234"

def main():
    print("Esta es una prueba del pre-commit hook")
    
if __name__ == "__main__":
    main()

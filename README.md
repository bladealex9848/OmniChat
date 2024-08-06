# OmniChat: Asistente Virtual Todo en Uno

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/bladealex1844/OmniChat?quickstart=1)

OmniChat es un asistente virtual versátil desarrollado con Langchain y Streamlit. Aprovecha el poder de los Modelos de Lenguaje (LLMs) para ofrecer una amplia gama de funcionalidades, simplificando la interacción con diversos tipos de información y bases de datos.

## 💬 Funcionalidades de OmniChat

OmniChat ofrece las siguientes capacidades:

- **Chatbot Básico**: 
  Mantén conversaciones interactivas con el LLM.
- **Chatbot Consciente del Contexto**: 
  Un asistente que recuerda conversaciones previas y proporciona respuestas acordes.
- **Chat con Documentos**: 
  Permite al chatbot acceder a documentos personalizados, respondiendo preguntas basadas en la información contenida.
- **Chat con Base de Datos SQL**: 
  Interactúa con bases de datos SQL mediante comandos conversacionales simples.
- **Chat con Sitios Web**: 
  Permite al chatbot interactuar con contenidos de sitios web.

## <img src="https://streamlit.io/images/brand/streamlit-mark-color.png" width="40" height="22"> Aplicación Streamlit

OmniChat es una aplicación multi-página desarrollada con Streamlit, que incluye todas las funcionalidades mencionadas.

Accede a la aplicación aquí: [OmniChat en Streamlit](https://omnichat-ai.streamlit.app)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://omnichat-ai.streamlit.app)

## 🖥️ Requisitos

- Python 3.10

## 🛠️ Configuración del Entorno Virtual (Python 3.10)

**1. Instalación de Python 3.10:**

* **Windows:**
  - Descarga el instalador de Python 3.10 desde [https://www.python.org/downloads/release/python-3109/](https://www.python.org/downloads/release/python-3109/) y asegúrate de marcar la casilla "Add Python 3.10 to PATH".
* **macOS (usando Homebrew):**
  - Instala Homebrew si aún no lo tienes: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
  - Luego instala Python 3.10: `brew install python@3.10`
* **Linux (usando el gestor de paquetes de tu distribución):**
  - Ejemplo para Debian/Ubuntu: `sudo apt-get install python3.10 python3.10-venv`

**2. Creación y Activación del Entorno Virtual:**

* Abre una terminal en la carpeta de tu proyecto.
* Crea el entorno virtual: `python3.10 -m venv mi_entorno_310`
* Activa el entorno virtual:
    - Windows: `mi_entorno_310\Scripts\activate`
    - macOS/Linux: `source mi_entorno_310/bin/activate`

**3. Actualización de pip:**

```
pip install --upgrade pip
```

**4. Instalación de Dependencias:**

```
pip install -r requirements.txt
```

# 🖥️ Ejecución Local
## Ejecutar la aplicación principal de Streamlit
```
$ python3 -m streamlit run Inicio.py # Si tienes Python 3.10 instalado en un entorno virtual
```
```
$ streamlit run Inicio.py # Si tienes Streamlit instalado globalmente
```

# 📦 Ejecución con Docker
## Generar la imagen
```
$ docker build -t omnichat .
```

## Ejecutar el contenedor Docker
```
$ docker run -p 8501:8501 omnichat
```

## 💁 Contribuciones
Planeamos añadir más funcionalidades a OmniChat con el tiempo. Las contribuciones son bienvenidas.

## 📄 Licencia
Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para obtener más detalles.
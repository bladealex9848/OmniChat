# OmniChat: Asistente Virtual Todo en Uno

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/bladealex1844/OmniChat?quickstart=1)

OmniChat es un asistente virtual versátil desarrollado con Langchain y Streamlit. Aprovecha el poder de los Modelos de Lenguaje (LLMs) para ofrecer una amplia gama de funcionalidades, simplificando la interacción con diversos tipos de información y bases de datos.

## 💬 Funcionalidades de OmniChat

OmniChat ofrece las siguientes capacidades:

- **Chatbot Básico**:
  Mantén conversaciones interactivas con el LLM.
- **Chatbot Consciente del Contexto**:
  Un asistente que recuerda conversaciones previas y proporciona respuestas acordes.
- **Chatbot con Acceso a Internet**:
  Equipado con acceso a internet, permite a los usuarios hacer preguntas sobre eventos recientes. Incluye sistema de respaldo gratuito (sin API keys) para búsquedas cuando DuckDuckGo alcanza límites de tasa.
- **Chat con Documentos**:
  Permite al chatbot acceder a documentos personalizados, respondiendo preguntas basadas en la información contenida.
- **Chat con Base de Datos SQL**:
  Interactúa con bases de datos SQL mediante comandos conversacionales simples.
- **Chat con Sitios Web**:
  Permite al chatbot interactuar con contenidos de sitios web.
- **Chat Multimodal con OpenRouter**:
  Analiza imágenes y responde preguntas sobre ellas usando modelos multimodales gratuitos de OpenRouter.
- **OCR con Mistral AI**:
  Extrae texto de imágenes y documentos PDF utilizando la API de OCR de Mistral AI.

## <img src="https://streamlit.io/images/brand/streamlit-mark-color.png" width="40" height="22"> Aplicación Streamlit

OmniChat es una aplicación multi-página desarrollada con Streamlit, que incluye todas las funcionalidades mencionadas.

Accede a la aplicación aquí: [OmniChat en Streamlit](https://omnichat-ai.streamlit.app)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://omnichat-ai.streamlit.app)

## 🖥️ Requisitos

- Python 3.13

## 🛠️ Configuración del Entorno Virtual (Python 3.13)

**1. Instalación de Python 3.13:**

* **Windows:**
  - Descarga el instalador de Python 3.13 desde [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/) y asegúrate de marcar la casilla "Add Python 3.13 to PATH".
* **macOS (usando Homebrew):**
  - Instala Homebrew si aún no lo tienes: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
  - Luego instala Python 3.10: `brew install python@3.13`
* **Linux (usando el gestor de paquetes de tu distribución):**
  - Ejemplo para Debian/Ubuntu: `sudo apt-get install python3.13 python3.13-venv`

**2. Creación y Activación del Entorno Virtual:**

* Abre una terminal en la carpeta de tu proyecto.
* Crea el entorno virtual: `python -m venv venv`
* Activa el entorno virtual:
    - Windows: `venv\Scripts\activate`
    - macOS/Linux: `source venv/bin/activate`

**3. Actualización de pip:**

```
pip install --upgrade pip
```

**4. Instalación de Dependencias:**

```
pip install -r requirements.txt
```

**5. Configuración de Claves API:**

Algunas funcionalidades requieren claves API para funcionar. Crea un archivo `.streamlit/secrets.toml` basado en el archivo de ejemplo `secrets.toml.example`:

```
# Copia el archivo de ejemplo
cp secrets.toml.example .streamlit/secrets.toml

# Edita el archivo con tus claves API
# Reemplaza los valores de ejemplo con tus propias claves
```

Las claves API necesarias son:
- **OPENAI_API_KEY**: Para los chatbots basados en OpenAI
- **OPENROUTER_API_KEY**: Para el chat multimodal con OpenRouter
- **MISTRAL_API_KEY**: Para OCR y procesamiento de documentos

# 🖥️ Ejecución Local
## Ejecutar la aplicación principal de Streamlit
```
$ python -m streamlit run Inicio.py # Si tienes Python 3.13 instalado en un entorno virtual
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
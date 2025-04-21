import streamlit as st
import os
import sys

# Añadir el directorio raíz al path para poder importar utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import utils

# Configurar la página directamente
st.set_page_config(
    page_title="OmniChat: Laboratorio de IA",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Mostrar el título
st.header("OmniChat: Laboratorio de Herramientas de IA")

# Mostrar información del autor
try:
    from sidebar_info import show_author_info
    show_author_info()
except ImportError:
    st.sidebar.warning("No se pudo cargar la información del autor.")

st.write(
    """
[![ver código fuente](https://img.shields.io/badge/Repositorio%20GitHub-gris?logo=github)](https://github.com/bladealex9848/OmniChat)
![Visitantes](https://api.visitorbadge.io/api/visitors?path=https%3A%2F%2Fomnichat.streamlit.app&label=Visitantes&labelColor=%235d5d5d&countColor=%231e7ebf&style=flat)
"""
)

# Información sobre el autor en la barra lateral
st.sidebar.markdown("### Desarrollado por")
st.sidebar.markdown("Alexander Oviedo Fadul")
st.sidebar.markdown(
    "[GitHub](https://github.com/bladealex9848) | [LinkedIn](https://www.linkedin.com/in/alexanderoviedo/)"
)

# Versión de la aplicación
st.sidebar.markdown("### Versión")
st.sidebar.markdown("v1.0.0")

# Enlaces útiles
st.sidebar.markdown("### Enlaces útiles")
st.sidebar.markdown("[Documentación de Mistral AI](https://docs.mistral.ai/)")
st.sidebar.markdown("[Documentación de Streamlit](https://docs.streamlit.io/)")
st.sidebar.markdown("[Documentación de OpenAI](https://platform.openai.com/docs)")


st.write(
    """
OmniChat es un asistente virtual versátil basado en Langchain, un poderoso framework diseñado para simplificar el desarrollo de aplicaciones utilizando Modelos de Lenguaje (LLMs). Langchain proporciona una integración completa de varios componentes, facilitando el proceso de ensamblarlos para crear aplicaciones robustas.

Aprovechando el poder de Langchain, la creación de chatbots se vuelve sencilla. Aquí hay algunos ejemplos de implementaciones de chatbot que atienden diferentes casos de uso:

- **Chatbot Básico**: Participa en conversaciones interactivas con el LLM.
- **Chatbot Consciente del Contexto**: Un chatbot que recuerda conversaciones previas y proporciona respuestas en consecuencia.
- **Chatbot con Acceso a Internet**: Un chatbot habilitado para internet capaz de responder consultas de usuarios sobre eventos recientes.
- **Chat con tus Documentos**: Potencia el chatbot con la capacidad de acceder a documentos personalizados, permitiéndole proporcionar respuestas a consultas de usuarios basadas en la información referenciada.
- **Chat con Base de Datos SQL**: Permite al chatbot interactuar con una base de datos SQL a través de comandos conversacionales simples.
- **Chat con Sitios Web**: Permite al chatbot interactuar con contenidos de sitios web.
- **Chat Multimodal**: Analiza imágenes y responde preguntas sobre ellas usando modelos multimodales gratuitos de OpenRouter.
- **OCR con Mistral AI**: Extrae texto de imágenes y documentos PDF utilizando la API de OCR de Mistral AI.

Para explorar ejemplos de uso de cada herramienta, por favor navega a la sección correspondiente en la barra lateral.
"""
)

# Sección sobre Mistral OCR
st.subheader("🔍 Mistral OCR - Nueva funcionalidad")

st.markdown(
    """
Este laboratorio ahora incluye una nueva herramienta para extracción de texto de imágenes y documentos PDF
usando la API de OCR (Reconocimiento Óptico de Caracteres) de Mistral AI.

### Características principales

- **Extracción de texto** de imágenes (JPG, PNG) y documentos PDF
- **Preservación de la estructura** y formato del texto extraído
- **Optimización automática** de imágenes para mejorar resultados
- **Descarga de resultados** en múltiples formatos (TXT, JSON, Markdown)
- **Sistema de respaldo** para búsquedas en internet cuando DuckDuckGo alcanza límites de tasa

### Limitaciones

- **Tamaño máximo de archivo**: 50 MB
- **Máximo de páginas por PDF**: 1,000 páginas
- **Formatos soportados**: PDF, JPG, PNG
- **Procesamiento desde URL**: En desarrollo
"""
)

# Mostrar información sobre el sistema de respaldo para búsquedas
with st.expander("ℹ️ Sistema de respaldo para búsquedas en internet"):
    st.markdown(
        """
    ### Sistema de búsqueda con respaldo automático

    Este laboratorio implementa un sistema de respaldo automático y transparente para búsquedas en internet:

    **Métodos gratuitos (primero):**
    1. **DuckDuckGo API** (método principal)
    2. **DuckDuckGo HTML** (respaldo gratuito)

    **APIs como respaldo:**
    3. **Google PSE API** (primera API de respaldo)
    4. **Exa API** (segunda API de respaldo)

    El sistema cambia automáticamente entre métodos de búsqueda cuando uno falla, sin mostrar errores al usuario.
    El sistema prioriza los métodos gratuitos y solo utiliza las APIs como respaldo si es necesario.

    Si todos los métodos fallan, el sistema proporcionará una respuesta basada en información básica almacenada,
    indicando que puede no estar completamente actualizada.
    """
    )

# La información del autor ya se muestra a través de utils.setup_page()

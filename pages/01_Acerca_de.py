import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Acerca de Mistral OCR",
    page_icon="ℹ️",
    layout="wide",
)

# Título principal
st.title("ℹ️ Acerca de Mistral OCR")

# Información sobre la aplicación
st.markdown("""
## ¿Qué es Mistral OCR?

Mistral OCR es una aplicación web que utiliza la API de OCR (Reconocimiento Óptico de Caracteres) 
de Mistral AI para extraer texto de imágenes y documentos PDF.

## Características principales

- **Extracción de texto** de imágenes (JPG, PNG) y documentos PDF
- **Preservación de la estructura** y formato del texto extraído
- **Optimización automática** de imágenes para mejorar resultados
- **Descarga de resultados** en múltiples formatos (TXT, JSON, Markdown)
- **Interfaz intuitiva** y fácil de usar

## Tecnologías utilizadas

- **Streamlit**: Framework para crear aplicaciones web interactivas con Python
- **Mistral AI API**: API de inteligencia artificial para OCR y procesamiento de documentos
- **Python**: Lenguaje de programación principal
- **PIL/Pillow**: Biblioteca para procesamiento de imágenes

## Limitaciones

- **Tamaño máximo de archivo**: 50 MB
- **Máximo de páginas por PDF**: 1,000 páginas
- **Formatos soportados**: PDF, JPG, PNG
- **Procesamiento desde URL**: En desarrollo

## Privacidad y seguridad

- Los documentos procesados no se almacenan permanentemente
- Los datos se envían a la API de Mistral AI para su procesamiento
- Consulta la [política de privacidad de Mistral AI](https://mistral.ai/privacy/) para más información
""")

# Información sobre el autor
st.sidebar.markdown("### Desarrollado por")
st.sidebar.markdown("Alexander Oviedo Fadul")
st.sidebar.markdown("[GitHub](https://github.com/bladealex9848) | [LinkedIn](https://www.linkedin.com/in/alexanderoviedo/)")

# Versión de la aplicación
st.sidebar.markdown("### Versión")
st.sidebar.markdown("v1.0.0")

# Enlaces útiles
st.sidebar.markdown("### Enlaces útiles")
st.sidebar.markdown("[Documentación de Mistral AI](https://docs.mistral.ai/)")
st.sidebar.markdown("[Documentación de Streamlit](https://docs.streamlit.io/)")

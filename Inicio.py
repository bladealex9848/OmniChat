import streamlit as st

st.set_page_config(
    page_title="OmniChat: Asistente Virtual", page_icon="🤖", layout="wide"
)

st.header("OmniChat: Asistente Virtual Todo en Uno")

st.write(
    """
[![ver código fuente](https://img.shields.io/badge/Repositorio%20GitHub-gris?logo=github)](https://github.com/bladealex9848/OmniChat)
![Visitantes](https://api.visitorbadge.io/api/visitors?path=https%3A%2F%2Fomnichat.streamlit.app&label=Visitantes&labelColor=%235d5d5d&countColor=%231e7ebf&style=flat)
"""
)

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

Para explorar ejemplos de uso de cada chatbot, por favor navega a la sección correspondiente del chatbot.
"""
)

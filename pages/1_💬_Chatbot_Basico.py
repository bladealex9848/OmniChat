import sys
import os

# Añadir el directorio raíz al path para poder importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils
import streamlit as st
from streaming import StreamHandler

from langchain.chains import ConversationChain

# Configurar la página directamente
st.set_page_config(page_title="Chatbot", page_icon="💬", layout="wide", initial_sidebar_state="expanded")

# Inicializar mensajes si no existen
if "basic_chat_messages" not in st.session_state:
    st.session_state["basic_chat_messages"] = [
        {
            "role": "assistant",
            "content": "Hola, soy un asistente virtual. ¿En qué puedo ayudarte hoy?",
        }
    ]

class BasicChatbot:

    def __init__(self):
        utils.sync_st_session()
        self.llm = utils.configure_llm()

    def setup_chain(self):
        chain = ConversationChain(llm=self.llm, verbose=True)
        return chain

    def main(self):
        # 1. Título y subtítulo (siempre visible en la parte superior)
        st.header("Chatbot Básico")
        st.write("Permite a los usuarios interactuar con el LLM")

        # Primero configurar el LLM en la barra lateral
        st.sidebar.markdown("### 🤖 Selecciona el modelo")
        self.llm = utils.configure_llm(key_suffix="_sidebar")

        # Luego mostrar instrucciones específicas para el chatbot básico
        with st.sidebar.expander("💬 Instrucciones de uso", expanded=True):
            st.markdown("""
            ### Cómo usar el Chatbot Básico

            1. **Selecciona un modelo** de lenguaje en la parte superior
            2. **Escribe tu pregunta** en el campo de texto inferior
            3. **Recibe respuestas** del asistente virtual

            #### Funcionalidades
            - Conversación simple pregunta-respuesta
            - Respuestas generadas en tiempo real
            - Interfaz de chat intuitiva

            #### Limitaciones
            - No tiene memoria de mensajes anteriores en la conversación
            - No tiene acceso a internet o documentos externos
            - No puede generar imágenes o procesar archivos
            """)

        # Mostrar información del autor en la barra lateral (al final)
        try:
            from sidebar_info import show_author_info
            show_author_info()
        except ImportError:
            st.sidebar.warning("No se pudo cargar la información del autor.")

        chain = self.setup_chain()

        # 2. Mostrar mensajes del historial (saludo inicial y conversación)
        for msg in st.session_state["basic_chat_messages"]:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        # 3. Campo de entrada para nuevas preguntas (al final)
        user_query = st.chat_input(placeholder="¡Hazme una pregunta!")
        if user_query:
            # Añadir mensaje del usuario al historial
            st.session_state["basic_chat_messages"].append({"role": "user", "content": user_query})

            # Mostrar mensaje del usuario (se mostrará en la próxima ejecución)
            with st.chat_message("user"):
                st.write(user_query)

            # Generar respuesta
            with st.chat_message("assistant"):
                st_cb = StreamHandler(st.empty())
                result = chain.invoke({"input": user_query}, {"callbacks": [st_cb]})
                response = result["response"]

                # Añadir respuesta al historial
                st.session_state["basic_chat_messages"].append(
                    {"role": "assistant", "content": response}
                )


if __name__ == "__main__":
    obj = BasicChatbot()
    obj.main()

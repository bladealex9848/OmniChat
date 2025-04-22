import sys
import os

# Añadir el directorio raíz al path para poder importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st

# Configuración de la página (debe ser la primera llamada a Streamlit)
st.set_page_config(
    page_title="Chatbot con Memoria",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

import utils
from streaming import StreamHandler

from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

# Inicializar mensajes si no existen
if "memory_chat_messages" not in st.session_state:
    st.session_state["memory_chat_messages"] = [
        {
            "role": "assistant",
            "content": "Hola, soy un asistente virtual. ¿En qué puedo ayudarte hoy?",
        }
    ]

class ContextChatbot:

    def __init__(self):
        utils.sync_st_session()
        self.llm = utils.configure_llm()

    @st.cache_resource
    def setup_chain(_self):
        memory = ConversationBufferMemory()
        chain = ConversationChain(llm=_self.llm, memory=memory, verbose=True)
        return chain

    def main(self):
        # 1. Título y subtítulo (siempre visible en la parte superior)
        st.header("Chatbot con Memoria")
        st.write(
            "Mejorando las interacciones del chatbot a través de la memoria de conversación"
        )

        # Mostrar información del autor en la barra lateral
        try:
            from sidebar_info import show_author_info
            show_author_info()
        except ImportError:
            st.sidebar.warning("No se pudo cargar la información del autor.")

        chain = self.setup_chain()

        # 2. Mostrar mensajes del historial (saludo inicial y conversación)
        for msg in st.session_state["memory_chat_messages"]:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        # 3. Campo de entrada para nuevas preguntas (al final)
        user_query = st.chat_input(placeholder="¡Hazme una pregunta!")
        if user_query:
            # Añadir mensaje del usuario al historial
            st.session_state["memory_chat_messages"].append({"role": "user", "content": user_query})

            # Mostrar mensaje del usuario (se mostrará en la próxima ejecución)
            with st.chat_message("user"):
                st.write(user_query)

            # Generar respuesta
            with st.chat_message("assistant"):
                st_cb = StreamHandler(st.empty())
                result = chain.invoke({"input": user_query}, {"callbacks": [st_cb]})
                response = result["response"]

                # Añadir respuesta al historial
                st.session_state["memory_chat_messages"].append(
                    {"role": "assistant", "content": response}
                )


if __name__ == "__main__":
    obj = ContextChatbot()
    obj.main()

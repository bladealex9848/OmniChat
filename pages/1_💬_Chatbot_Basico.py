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


class BasicChatbot:

    def __init__(self):
        utils.sync_st_session()
        self.llm = utils.configure_llm()

    def setup_chain(self):
        chain = ConversationChain(llm=self.llm, verbose=True)
        return chain

    @utils.enable_chat_history
    def main(self):
        # Usar contenedores para organizar la interfaz
        header_container = st.container()
        chat_container = st.container()

        # Contenedor del encabezado (siempre visible en la parte superior)
        with header_container:
            st.header("Chatbot Básico")
            st.write("Permite a los usuarios interactuar con el LLM")

        # Mostrar información del autor
        try:
            from sidebar_info import show_author_info
            show_author_info()
        except ImportError:
            st.sidebar.warning("No se pudo cargar la información del autor.")

        chain = self.setup_chain()

        # Interfaz de chat en el contenedor de chat
        with chat_container:
            user_query = st.chat_input(placeholder="¡Hazme una pregunta!")
            if user_query:
                utils.display_msg(user_query, "user")
                with st.chat_message("assistant"):
                    st_cb = StreamHandler(st.empty())
                    result = chain.invoke({"input": user_query}, {"callbacks": [st_cb]})
                    response = result["response"]
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response}
                    )


if __name__ == "__main__":
    obj = BasicChatbot()
    obj.main()

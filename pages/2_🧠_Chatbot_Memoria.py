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

# Encabezado
st.header("Chatbot con Memoria")
st.write(
    "Mejorando las interacciones del chatbot a través de la memoria de conversación"
)

# Mostrar información del autor
try:
    from sidebar_info import show_author_info
    show_author_info()
except ImportError:
    st.sidebar.warning("No se pudo cargar la información del autor.")


class ContextChatbot:

    def __init__(self):
        utils.sync_st_session()
        self.llm = utils.configure_llm()

    @st.cache_resource
    def setup_chain(_self):
        memory = ConversationBufferMemory()
        chain = ConversationChain(llm=_self.llm, memory=memory, verbose=True)
        return chain

    @utils.enable_chat_history
    def main(self):
        chain = self.setup_chain()
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
    obj = ContextChatbot()
    obj.main()

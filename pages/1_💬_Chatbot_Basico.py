import sys
import os

# Añadir el directorio raíz al path para poder importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils
import streamlit as st
from streaming import StreamHandler

from langchain.chains import ConversationChain

# Usar la función setup_page para configurar la página de manera consistente
utils.setup_page("Chatbot Básico", "💬", "Chatbot")
st.write("Permite a los usuarios interactuar con el LLM")


class BasicChatbot:

    def __init__(self):
        utils.sync_st_session()
        self.llm = utils.configure_llm()

    def setup_chain(self):
        chain = ConversationChain(llm=self.llm, verbose=True)
        return chain

    @utils.enable_chat_history
    def main(self):
        chain = self.setup_chain()
        # user_query = st.chat_input(placeholder="Ask me anything!")
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

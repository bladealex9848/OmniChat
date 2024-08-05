import utils
import streamlit as st

from langchain import hub
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import Tool

# Encabezado en Inglés
# st.set_page_config(page_title="ChatNet", page_icon="🌐")
# st.header('Chatbot with Internet Access')
# st.write('Equipped with internet access, enables users to ask questions about recent events')

# Encabezado en Español
st.set_page_config(page_title="ChatNet", page_icon="🌐")
st.header('Chatbot con Acceso a Internet')
st.write('Equipado con acceso a internet, permite a los usuarios hacer preguntas sobre eventos recientes')


class InternetChatbot:

    def __init__(self):
        utils.sync_st_session()
        self.llm = utils.configure_llm()

    # @st.cache_resource(show_spinner='Connecting..')
    def setup_agent(_self):
        # Define tool
        # Definir herramienta
        ddg_search = DuckDuckGoSearchRun()
        tools = [
            Tool(
                name="DuckDuckGoSearch",
                func=ddg_search.run,
                # description="Useful for when you need to answer questions about current events. You should ask targeted questions",
                description="Útil cuando necesitas responder preguntas sobre eventos actuales. Debes hacer preguntas específicas",
            )
        ]

        # Get the prompt - can modify this
        # Obtener el prompt - se puede modificar
        prompt = hub.pull("hwchase17/react-chat")

        # Setup LLM and Agent
        # Configurar LLM y Agente
        memory = ConversationBufferMemory(memory_key="chat_history")
        agent = create_react_agent(_self.llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True)
        return agent_executor, memory

    @utils.enable_chat_history
    def main(self):
        agent_executor, memory = self.setup_agent()
        # user_query = st.chat_input(placeholder="Ask me anything!")
        user_query = st.chat_input(placeholder="¡Hazme una pregunta!")
        if user_query:
            utils.display_msg(user_query, 'user')
            with st.chat_message("assistant"):
                st_cb = StreamlitCallbackHandler(st.container())
                result = agent_executor.invoke(
                    {"input": user_query, "chat_history": memory.chat_memory.messages},
                    {"callbacks": [st_cb]}
                )
                response = result["output"]
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.write(response)

if __name__ == "__main__":
    obj = InternetChatbot()
    obj.main()
import utils
import streamlit as st
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import Tool

st.set_page_config(page_title="ChatNet", page_icon="🌐")
st.header('Chatbot con Acceso a Internet')
st.write('Equipado con acceso a internet, permite a los usuarios hacer preguntas sobre eventos recientes')

class InternetChatbot:
    def __init__(self):
        utils.sync_st_session()
        self.llm = utils.configure_llm()

    def setup_agent(self):
        # Define tool
        ddg_search = DuckDuckGoSearchRun()
        tools = [
            Tool(
                name="DuckDuckGoSearch",
                func=ddg_search.run,
                description="Útil cuando necesitas responder preguntas sobre eventos actuales. Debes hacer preguntas específicas",
            )
        ]

        # Get the prompt - can modify this
        prompt = hub.pull("hwchase17/react-chat")

        # Setup LLM and Agent
        memory = ConversationBufferMemory(memory_key="chat_history")
        agent = create_react_agent(self.llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True)
        return agent_executor, memory

    @utils.enable_chat_history
    def main(self):
        agent_executor, memory = self.setup_agent()
        user_query = st.chat_input(placeholder="¡Hazme una pregunta!")
        if user_query:
            utils.display_msg(user_query, 'user')
            with st.chat_message("assistant"):
                st_cb = StreamlitCallbackHandler(st.container())
                try:
                    result = agent_executor.invoke(
                        {"input": user_query, "chat_history": memory.chat_memory.messages},
                        {"callbacks": [st_cb]}
                    )
                    response = result["output"]
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.write(response)
                except Exception as e:
                    error_msg = f"Lo siento, ocurrió un error: {str(e)}. Por favor, intenta reformular tu pregunta."
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

if __name__ == "__main__":
    obj = InternetChatbot()
    obj.main()
import sys
import os

# Añadir el directorio raíz al path para poder importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils
import streamlit as st
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import Tool

# Importar herramienta de búsqueda con respaldo
import search_utils

st.set_page_config(page_title="ChatNet", page_icon="🌐")
st.header("Chatbot con Acceso a Internet")
st.write(
    "Equipado con acceso a internet, permite a los usuarios hacer preguntas sobre eventos recientes"
)


class InternetChatbot:
    def __init__(self):
        utils.sync_st_session()
        self.llm = utils.configure_llm()

    def setup_agent(self):
        # Definir herramientas de búsqueda
        try:
            # Intentar usar DuckDuckGo primero
            ddg_search = DuckDuckGoSearchRun()
            search_tool = Tool(
                name="DuckDuckGoSearch",
                func=ddg_search.run,
                description="Útil cuando necesitas responder preguntas sobre eventos actuales. Debes hacer preguntas específicas",
            )
        except Exception as e:
            st.warning(
                f"Error al configurar DuckDuckGo: {str(e)}. Usando herramienta de búsqueda alternativa."
            )
            # Usar nuestra herramienta de búsqueda con respaldo
            fallback_search = search_utils.get_search_tool()
            search_tool = Tool(
                name="InternetSearch",
                func=fallback_search.run,
                description="Útil cuando necesitas responder preguntas sobre eventos actuales. Debes hacer preguntas específicas",
            )

        # No usamos Google Search API porque requiere API key
        # En su lugar, usamos métodos de scraping gratuitos implementados en search_utils.py
        tools = [search_tool]

        # Get the prompt - can modify this
        prompt = hub.pull("hwchase17/react-chat")

        # Setup LLM and Agent
        memory = ConversationBufferMemory(memory_key="chat_history")
        agent = create_react_agent(self.llm, tools, prompt)
        agent_executor = AgentExecutor(
            agent=agent, tools=tools, memory=memory, verbose=True
        )
        return agent_executor, memory

    @utils.enable_chat_history
    def main(self):
        # Mostrar información sobre las herramientas de búsqueda alternativas
        with st.sidebar.expander("ℹ️ Información sobre búsquedas"):
            st.markdown(
                """
            ### Herramientas de búsqueda gratuitas

            Este chatbot utiliza múltiples herramientas de búsqueda gratuitas con un sistema de respaldo:

            1. **DuckDuckGo** (principal)
            2. **Google** (respaldo mediante scraping)
            3. **Bing** (respaldo mediante scraping)
            4. **DuckDuckGo HTML** (respaldo final mediante scraping)

            Si experimentas errores de "rate limit", el sistema intentará usar automáticamente los métodos alternativos.

            > **Nota**: Todos los métodos de búsqueda son gratuitos y no requieren API keys.
            """
            )

            # Consejos para mejorar las búsquedas
            st.subheader("Consejos para mejorar las búsquedas")
            st.markdown(
                """
            - Haz preguntas específicas y concretas
            - Incluye fechas, nombres completos y detalles relevantes
            - Evita preguntas muy generales
            - Si recibes un error de límite de tasa, espera unos minutos e intenta de nuevo
            - Reformula tu pregunta si no obtienes resultados satisfactorios
            """
            )

        # Configurar el agente con manejo de errores
        try:
            agent_executor, memory = self.setup_agent()
        except Exception as e:
            st.error(f"Error al configurar el agente: {str(e)}")
            st.info("Intenta recargar la página o verifica tu conexión a internet.")
            st.stop()

        # Interfaz de chat
        user_query = st.chat_input(
            placeholder="¡Hazme una pregunta sobre eventos actuales!"
        )
        if user_query:
            utils.display_msg(user_query, "user")
            with st.chat_message("assistant"):
                st_cb = StreamlitCallbackHandler(st.container())
                try:
                    # Mostrar indicador de carga
                    with st.status("Buscando información...", expanded=False) as status:
                        result = agent_executor.invoke(
                            {
                                "input": user_query,
                                "chat_history": memory.chat_memory.messages,
                            },
                            {"callbacks": [st_cb]},
                        )
                        response = result["output"]
                        status.update(
                            label="¡Información encontrada!", state="complete"
                        )

                    # Mostrar respuesta
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response}
                    )
                    st.write(response)

                except Exception as e:
                    # Manejar diferentes tipos de errores
                    if "RatelimitException" in str(e) or "rate limit" in str(e).lower():
                        error_msg = f"Lo siento, se ha alcanzado el límite de consultas en los servicios de búsqueda. Por favor, intenta de nuevo en unos minutos o reformula tu pregunta de manera más específica."
                    elif "timeout" in str(e).lower():
                        error_msg = f"Lo siento, la búsqueda ha tardado demasiado tiempo. Por favor, intenta con una pregunta más específica."
                    elif "connection" in str(e).lower():
                        error_msg = f"Lo siento, hay problemas de conexión. Por favor, verifica tu conexión a internet e intenta de nuevo."
                    else:
                        error_msg = f"Lo siento, ocurrió un error: {str(e)}. Por favor, intenta reformular tu pregunta."

                    st.error(error_msg)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_msg}
                    )

                    # Sugerencias para el usuario
                    st.info(
                        """
                    **Sugerencias para mejorar las búsquedas:**
                    - Haz preguntas más específicas
                    - Incluye fechas o nombres completos
                    - Evita preguntas muy generales
                    - Espera unos minutos si hay errores de límite de consultas
                    """
                    )


if __name__ == "__main__":
    obj = InternetChatbot()
    obj.main()

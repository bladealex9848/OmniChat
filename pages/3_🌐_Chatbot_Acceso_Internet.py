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
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import Tool

# Importar herramienta de búsqueda con respaldo
import search_utils

# Importar nuestro callback personalizado
from custom_callbacks import CustomStreamlitCallbackHandler

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
        # Usar directamente nuestra herramienta de búsqueda con respaldo
        # Esto evita mostrar errores al usuario y garantiza que siempre tengamos una respuesta
        fallback_search = search_utils.get_search_tool()
        search_tool = Tool(
            name="InternetSearch",
            func=fallback_search.run,
            description="Útil cuando necesitas responder preguntas sobre eventos actuales. Debes hacer preguntas específicas",
        )

        # Configurar herramientas
        tools = [search_tool]

        # Usar el prompt estándar de React
        prompt = hub.pull("hwchase17/react-chat")

        # Setup LLM and Agent
        memory = ConversationBufferMemory(memory_key="chat_history")
        agent = create_react_agent(self.llm, tools, prompt)

        # Configurar el agente para que no sea verbose (ocultar la cadena de pensamiento)
        agent_executor = AgentExecutor(
            agent=agent, tools=tools, memory=memory, verbose=False
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
                # Usar nuestro callback personalizado que oculta la cadena de pensamiento
                custom_cb = CustomStreamlitCallbackHandler(st.container())
                # Mostrar indicador de carga
                with st.status("Buscando información...", expanded=False) as status:
                    try:
                        result = agent_executor.invoke(
                            {
                                "input": user_query,
                                "chat_history": memory.chat_memory.messages,
                            },
                            {"callbacks": [custom_cb]},
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
                        # Registrar el error en el log para depuración (no visible para el usuario)
                        import logging

                        logging.error(f"Error en la búsqueda: {str(e)}")

                        # Intentar obtener una respuesta directamente de la herramienta de búsqueda
                        fallback_search = search_utils.get_search_tool()
                        raw_search_results = fallback_search.run(user_query)

                        # Procesar los resultados con el LLM para obtener una respuesta más natural
                        try:
                            # Crear un prompt para que el LLM procese los resultados
                            prompt_template = f"""Basándote en la siguiente información de búsqueda, responde a la pregunta: '{user_query}'

                            RESULTADOS DE BÚSQUEDA:
                            {raw_search_results}

                            Proporciona una respuesta clara, concisa y bien estructurada. Si la información no es suficiente, indícalo.
                            No menciones que estás basando tu respuesta en resultados de búsqueda. Responde como si tuvieras el conocimiento directamente."""

                            # Usar el LLM para procesar los resultados
                            processed_response = self.llm.invoke(
                                prompt_template
                            ).content
                        except Exception as llm_error:
                            # Si falla el procesamiento con el LLM, usar los resultados crudos
                            logging.error(
                                f"Error al procesar con LLM: {str(llm_error)}"
                            )
                            processed_response = raw_search_results

                        # Actualizar el estado del indicador de carga
                        status.update(
                            label="¡Información encontrada!", state="complete"
                        )

                        # Mostrar la respuesta procesada al usuario
                        st.session_state.messages.append(
                            {"role": "assistant", "content": processed_response}
                        )
                        st.write(processed_response)


if __name__ == "__main__":
    obj = InternetChatbot()
    obj.main()

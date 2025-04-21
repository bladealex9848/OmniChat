import sys
import os

# Añadir el directorio raíz al path para poder importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st

# Configuración de la página (debe ser la primera llamada a Streamlit)
st.set_page_config(
    page_title="ChatNet",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

import utils
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import Tool

# Importar funciones de búsqueda con respaldo
from search_services import perform_web_search, format_search_results

# Importar nuestro callback personalizado
from custom_callbacks import CustomStreamlitCallbackHandler


class InternetChatbot:
    def __init__(self):
        utils.sync_st_session()
        self.llm = utils.configure_llm()

    def setup_agent(self):
        # Crear una función de búsqueda que utiliza perform_web_search y format_search_results
        def search_function(query: str) -> str:
            # Realizar la búsqueda utilizando los métodos que funcionan correctamente
            search_results = perform_web_search(query)
            if search_results:
                # Formatear los resultados para que sean legibles
                return format_search_results(search_results)
            else:
                return "No se encontraron resultados para la consulta."

        # Crear la herramienta de búsqueda
        search_tool = Tool(
            name="InternetSearch",
            func=search_function,
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
        # La configuración de la página ya se ha realizado al inicio del script
        st.header("Chatbot con Acceso a Internet")
        st.write(
            "Equipado con acceso a internet, permite a los usuarios hacer preguntas sobre eventos recientes"
        )

        # Mostrar información del autor
        try:
            from sidebar_info import show_author_info
            show_author_info()
        except ImportError:
            st.sidebar.warning("No se pudo cargar la información del autor.")

        # Mostrar información sobre las herramientas de búsqueda alternativas
        with st.sidebar.expander("ℹ️ Información sobre búsquedas"):
            st.markdown(
                """
            ### Sistema de búsqueda con respaldo automático

            Este chatbot utiliza múltiples herramientas de búsqueda con un sistema de respaldo:

            **Métodos gratuitos (primero):**
            1. **DuckDuckGo API** (método principal)
            2. **DuckDuckGo HTML** (respaldo gratuito)

            **APIs como respaldo:**
            3. **Google PSE API** (primera API de respaldo)
            4. **Exa API** (segunda API de respaldo)

            Si experimentas errores de "rate limit", el sistema intentará usar automáticamente los métodos alternativos.

            > **Nota**: El sistema prioriza los métodos gratuitos y solo utiliza las APIs como respaldo si es necesario.
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
            # Mostrar indicador de carga
            with st.status("Buscando información...", expanded=True) as status:
                try:
                    # Añadir la pregunta del usuario al historial
                    utils.display_msg(user_query, "user")

                    # Intentar obtener respuesta usando el agente
                    result = agent_executor.invoke(
                        {
                            "input": user_query,
                            "chat_history": memory.chat_memory.messages,
                        }
                    )
                    response = result["output"]

                    # Mostrar la cadena de pensamiento en el indicador de carga
                    if "intermediate_steps" in result:
                        for step in result["intermediate_steps"]:
                            if hasattr(step[0], "tool") and hasattr(step[0], "tool_input"):
                                status.write(f"**Acción:** {step[0].tool}")
                                status.write(f"**Entrada:** {step[0].tool_input}")
                                status.write(f"**Resultado:** {step[1]}")

                except Exception as e:
                    # Si falla el agente, usar búsqueda directa
                    import logging
                    logging.error(f"Error en la búsqueda: {str(e)}")

                    # Buscar información
                    status.write("Usando búsqueda directa como alternativa...")
                    search_results = perform_web_search(user_query)
                    raw_search_results = format_search_results(search_results) if search_results else "No se encontraron resultados para la consulta."

                    # Mostrar resultados de búsqueda en el indicador de carga
                    status.write("Resultados de búsqueda:")
                    status.write(raw_search_results[:500] + "..." if len(raw_search_results) > 500 else raw_search_results)

                    # Procesar los resultados con el LLM
                    try:
                        status.write("Procesando resultados...")
                        prompt_template = f"""Basándote en la siguiente información de búsqueda, responde a la pregunta: '{user_query}'

                        RESULTADOS DE BÚSQUEDA:
                        {raw_search_results}

                        Proporciona una respuesta clara, concisa y bien estructurada. Si la información no es suficiente, indícalo.
                        No menciones que estás basando tu respuesta en resultados de búsqueda. Responde como si tuvieras el conocimiento directamente."""

                        # Usar el LLM para procesar los resultados
                        response = self.llm.invoke(prompt_template).content
                    except Exception as llm_error:
                        # Si falla el procesamiento con el LLM, usar los resultados crudos
                        logging.error(f"Error al procesar con LLM: {str(llm_error)}")
                        response = raw_search_results

                # Actualizar el estado del indicador de carga
                status.update(label="¡Información encontrada!", state="complete")

            # Añadir la respuesta al historial
            utils.display_msg(response, "assistant")

            # Recargar la página para mostrar el historial actualizado
            st.rerun()


if __name__ == "__main__":
    obj = InternetChatbot()
    obj.main()

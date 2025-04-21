import sys
import os

# Añadir el directorio raíz al path para poder importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils
import streamlit as st
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import Tool

# Importar funciones de búsqueda con respaldo
from search_services import perform_web_search, format_search_results

# Importar nuestro callback personalizado
from custom_callbacks import CustomStreamlitCallbackHandler

# La configuración de la página se ha movido al método main


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
        # Configuración de la página usando la función centralizada
        utils.setup_page(
            "Chatbot con Acceso a Internet",
            "🌐",
            "ChatNet"
        )
        st.write(
            "Equipado con acceso a internet, permite a los usuarios hacer preguntas sobre eventos recientes"
        )

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
            utils.display_msg(user_query, "user")
            with st.chat_message("assistant"):
                # Crear un contenedor para la cadena de pensamiento (oculto por defecto)
                thought_container = st.container()
                # Usar nuestro callback personalizado que oculta la cadena de pensamiento
                custom_cb = CustomStreamlitCallbackHandler(thought_container)
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

                        # La respuesta ya se muestra en el callback personalizado
                        # Solo guardamos el mensaje en el historial
                        st.session_state.messages.append(
                            {"role": "assistant", "content": response}
                        )
                        # No es necesario mostrar la respuesta aquí, ya se muestra en el callback

                    except Exception as e:
                        # Registrar el error en el log para depuración (no visible para el usuario)
                        import logging

                        logging.error(f"Error en la búsqueda: {str(e)}")

                        # Intentar obtener una respuesta directamente utilizando perform_web_search
                        search_results = perform_web_search(user_query)
                        raw_search_results = format_search_results(search_results) if search_results else "No se encontraron resultados para la consulta."

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
                        # Mostrar la respuesta (en este caso sí es necesario porque no usamos el callback)
                        st.markdown(processed_response)


if __name__ == "__main__":
    obj = InternetChatbot()
    obj.main()

"""
Utilidades para el manejo de chat en Streamlit.
"""

try:
    import streamlit as st
except ImportError:
    # Para pruebas sin streamlit
    class StMock:
        def __init__(self):
            self.session_state = {}

        def cache_resource(self):
            pass

        def chat_message(self, role):
            class Writer:
                def write(self, content):
                    print(f"[{role}]: {content}")
            return Writer()

    st = StMock()

# decorator
# Decorador para habilitar el historial de chat
def enable_chat_history(func):
    def execute(*args, **kwargs):
        # to clear chat history after switching chatbot
        # Limpiar el historial del chat después de cambiar el chatbot
        current_page = func.__qualname__
        if "current_page" not in st.session_state:
            st.session_state["current_page"] = current_page
        if st.session_state["current_page"] != current_page:
            try:
                st.cache_resource.clear()
                del st.session_state["current_page"]
                del st.session_state["messages"]
            except:
                pass

        # Inicializar mensajes si no existen
        if "messages" not in st.session_state:
            st.session_state["messages"] = [
                {
                    "role": "assistant",
                    "content": "Hola, soy un asistente virtual. ¿En qué puedo ayudarte hoy?",
                }
            ]

        # Ejecutar la función decorada PRIMERO (para mostrar encabezados y manejar la lógica de la página)
        result = func(*args, **kwargs)

        # DESPUÉS mostrar todos los mensajes del historial, excepto el saludo inicial
        # Esto asegura que el título aparezca antes que los mensajes

        # Mostrar el saludo inicial solo si no hay otros mensajes
        if len(st.session_state["messages"]) == 1 and st.session_state["messages"][0]["role"] == "assistant" and "Hola, soy un asistente virtual" in st.session_state["messages"][0]["content"]:
            with st.chat_message("assistant"):
                st.write(st.session_state["messages"][0]["content"])
        else:
            # Filtrar el mensaje de saludo si hay más mensajes
            filtered_messages = [msg for msg in st.session_state["messages"]
                               if not (msg["role"] == "assistant" and "Hola, soy un asistente virtual" in msg["content"])
                               or len(st.session_state["messages"]) == 1]

            # Mostrar los mensajes filtrados
            for msg in filtered_messages:
                with st.chat_message(msg["role"]):
                    # Verificar si el mensaje contiene una cadena de pensamiento
                    if msg["role"] == "assistant" and "---" in msg["content"]:
                        # Separar la respuesta de la cadena de pensamiento
                        parts = msg["content"].split("---", 1)
                        # Mostrar solo la respuesta principal
                        st.write(parts[0].strip())

                        # Mostrar la cadena de pensamiento en un expansor contraído
                        with st.expander("Cadena de pensamiento", expanded=False):
                            st.markdown(parts[1].strip())
                    else:
                        # Mostrar el mensaje completo si no tiene cadena de pensamiento
                        st.write(msg["content"])

        return result

    return execute


def display_msg(msg, author):
    """Method to display message on the UI

    Args:
        msg (str): message to display
        author (str): author of the message -user/assistant
    """
    """
    Método para mostrar mensaje en la interfaz de usuario

    Args:
        msg (str): mensaje a mostrar
        author (str): autor del mensaje -usuario/asistente
    """
    # Solo añadir el mensaje al historial
    # No mostrarlo directamente, ya que el decorador enable_chat_history se encarga de mostrar todos los mensajes
    st.session_state.messages.append({"role": author, "content": msg})


def sync_st_session():
    """
    Sincroniza el estado de la sesión de Streamlit.
    Esto es útil para asegurar que todos los valores de la sesión estén actualizados.
    """
    for k, v in st.session_state.items():
        st.session_state[k] = v

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

        # Ejecutar la función decorada (para mostrar encabezados y manejar la lógica de la página)
        result = func(*args, **kwargs)

        # Mostrar el mensaje de bienvenida solo si es la primera carga de la página
        # y no hay más mensajes en el historial
        if len(st.session_state["messages"]) == 1 and st.session_state["messages"][0]["role"] == "assistant":
            # Mostrar el mensaje de bienvenida después de los encabezados
            st.chat_message("assistant").write(st.session_state["messages"][0]["content"])

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
    # Añadir el mensaje al historial
    st.session_state.messages.append({"role": author, "content": msg})
    # Mostrar el mensaje en la interfaz
    st.chat_message(author).write(msg)


def sync_st_session():
    """
    Sincroniza el estado de la sesión de Streamlit.
    Esto es útil para asegurar que todos los valores de la sesión estén actualizados.
    """
    for k, v in st.session_state.items():
        st.session_state[k] = v

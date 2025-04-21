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

        # to show chat history on ui
        # Mostrar el historial del chat en la interfaz de usuario
        if "messages" not in st.session_state:
            st.session_state["messages"] = [
                {
                    "role": "assistant",
                    "content": "Hola, soy un asistente virtual. ¿En qué puedo ayudarte hoy?",
                }
            ]
        for msg in st.session_state["messages"]:
            st.chat_message(msg["role"]).write(msg["content"])

        # Ejecutar la función decorada
        return func(*args, **kwargs)

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
    st.session_state.messages.append({"role": author, "content": msg})
    st.chat_message(author).write(msg)

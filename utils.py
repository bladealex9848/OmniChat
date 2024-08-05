import os
import openai
import streamlit as st
from datetime import datetime
from langchain_openai import ChatOpenAI

#decorator
# Decorador para habilitar el historial de chat
def enable_chat_history(func):
    if os.environ.get("OPENAI_API_KEY"):

        # to clear chat history after swtching chatbot
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
            st.session_state["messages"] = [{"role": "assistant", "content": "Hola, soy un asistente virtual. ¿En qué puedo ayudarte hoy?"}]
        for msg in st.session_state["messages"]:
            st.chat_message(msg["role"]).write(msg["content"])

    def execute(*args, **kwargs):
        func(*args, **kwargs)
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

def choose_custom_openai_key():
    openai_api_key = st.sidebar.text_input(
        label="OpenAI API Key",
        type="password",
        placeholder="sk-...",
        key="SELECTED_OPENAI_API_KEY"
        )
    if not openai_api_key:
        # st.error("Please add your OpenAI API key to continue.")
        st.error("Por favor, añade tu clave de API de OpenAI para continuar.")
        # st.info("Obtain your key from this link: https://platform.openai.com/account/api-keys")
        st.info("Obtén tu clave de este enlace: https://platform.openai.com/account/api-keys")
        st.stop()

    model = "gpt-4o-mini"
    try:
        client = openai.OpenAI(api_key=openai_api_key)
        available_models = [{"id": i.id, "created":datetime.fromtimestamp(i.created)} for i in client.models.list() if str(i.id).startswith("gpt")]
        available_models = sorted(available_models, key=lambda x: x["created"])
        available_models = [i["id"] for i in available_models]

        model = st.sidebar.selectbox(
            label="Model",
            options=available_models,
            key="SELECTED_OPENAI_MODEL"
        )
    except openai.AuthenticationError as e:
        st.error(e.body["message"])
        st.stop()
    except Exception as e:
        print(e)
        # st.error("Something went wrong. Please try again later.")
        st.error("Algo salió mal. Por favor, inténtalo de nuevo más tarde.")
        st.stop()
    return model, openai_api_key

def configure_llm():
    # available_llms = ["gpt-4o-mini","llama3.1:8b","use your openai api key"]
    available_llms = ["gpt-4o-mini","usa tu clave de api de openai"]
    llm_opt = st.sidebar.radio(
        label="LLM",
        options=available_llms,
        key="SELECTED_LLM"
        )
    
    if llm_opt == "gpt-4o-mini":
        llm = ChatOpenAI(model_name=llm_opt, temperature=0, streaming=True, api_key=st.secrets["OPENAI_API_KEY"])
    else:
        model, openai_api_key = choose_custom_openai_key()
        llm = ChatOpenAI(model_name=model, temperature=0, streaming=True, api_key=openai_api_key)
    return llm

def sync_st_session():
    for k, v in st.session_state.items():
        st.session_state[k] = v
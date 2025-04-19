import os
import json
import openai
import requests
import streamlit as st
from datetime import datetime
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI


# decorator
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
            st.session_state["messages"] = [
                {
                    "role": "assistant",
                    "content": "Hola, soy un asistente virtual. ¿En qué puedo ayudarte hoy?",
                }
            ]
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
        key="SELECTED_OPENAI_API_KEY",
    )
    if not openai_api_key:
        # st.error("Please add your OpenAI API key to continue.")
        st.error("Por favor, añade tu clave de API de OpenAI para continuar.")
        # st.info("Obtain your key from this link: https://platform.openai.com/account/api-keys")
        st.info(
            "Obtén tu clave de este enlace: https://platform.openai.com/account/api-keys"
        )
        st.stop()

    model = "gpt-4o-mini"
    try:
        client = openai.OpenAI(api_key=openai_api_key)
        available_models = [
            {"id": i.id, "created": datetime.fromtimestamp(i.created)}
            for i in client.models.list()
            if str(i.id).startswith("gpt")
        ]
        available_models = sorted(available_models, key=lambda x: x["created"])
        available_models = [i["id"] for i in available_models]

        model = st.sidebar.selectbox(
            label="Model", options=available_models, key="SELECTED_OPENAI_MODEL"
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
    available_llms = ["gpt-4.1-nano", "openrouter", "usa tu clave de api de openai"]
    llm_opt = st.sidebar.radio(label="LLM", options=available_llms, key="SELECTED_LLM")

    if llm_opt == "gpt-4.1-nano":
        # Usar el modelo predeterminado con la clave API de OpenAI de secrets.toml
        if not hasattr(st, "secrets") or "OPENAI_API_KEY" not in st.secrets:
            st.error("No se encontró la clave API de OpenAI en secrets.toml")
            st.info(
                "Por favor, usa otra opción de modelo o configura la clave API en secrets.toml"
            )
            st.stop()

        llm = ChatOpenAI(
            model_name=llm_opt,
            temperature=0,
            streaming=True,
            api_key=st.secrets["OPENAI_API_KEY"],
        )
    elif llm_opt == "openrouter":
        # Configurar cliente de OpenRouter
        api_key, model_id = configure_openrouter_client()

        # Crear cliente de OpenAI pero con la base_url de OpenRouter
        llm = ChatOpenAI(
            model=model_id,
            temperature=0,
            streaming=True,
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://github.com/bladealex9848/OmniChat",
                "X-Title": "OmniChat",
            },
        )
    else:
        # Usar clave API personalizada de OpenAI
        model, openai_api_key = choose_custom_openai_key()
        llm = ChatOpenAI(
            model_name=model, temperature=0, streaming=True, api_key=openai_api_key
        )
    return llm


def sync_st_session():
    for k, v in st.session_state.items():
        st.session_state[k] = v


def get_openrouter_free_models() -> List[Dict[str, Any]]:
    """
    Obtiene la lista de modelos multimodales GRATUITOS disponibles en OpenRouter
    o modelos que tengan "free" en su nombre o descripción.

    Returns:
        List[Dict[str, Any]]: Lista de modelos gratuitos con sus detalles
    """
    # Lista de modelos por defecto conocidos por ser gratuitos
    default_models = [
        # Modelos multimodales gratuitos
        {
            "id": "meta-llama/llama-4-maverick:free",
            "name": "Llama 4 Maverick (Free)",
            "description": "Modelo multimodal de Meta con capacidades avanzadas de visión y razonamiento",
            "context_length": 128000,
            "multimodal": True,
            "free": True,
        },
        {
            "id": "meta-llama/llama-4-scout:free",
            "name": "Llama 4 Scout (Free)",
            "description": "Modelo multimodal de Meta optimizado para eficiencia y razonamiento visual",
            "context_length": 128000,
            "multimodal": True,
            "free": True,
        },
        {
            "id": "qwen/qwen2.5-vl-32b-instruct:free",
            "name": "Qwen 2.5 VL 32B (Free)",
            "description": "Modelo multimodal de Qwen con soporte para visión y múltiples idiomas",
            "context_length": 32000,
            "multimodal": True,
            "free": True,
        },
        {
            "id": "qwen/qwen2.5-vl-72b-instruct:free",
            "name": "Qwen 2.5 VL 72B (Free)",
            "description": "Versión más grande del modelo multimodal de Qwen con mayor capacidad",
            "context_length": 32000,
            "multimodal": True,
            "free": True,
        },
        # Modelos de texto gratuitos de alta calidad
        {
            "id": "google/gemini-2.0-flash-thinking-exp:free",
            "name": "Gemini 2.0 Flash (Free)",
            "description": "Modelo rápido de Google con razonamiento avanzado",
            "context_length": 32000,
            "multimodal": False,
            "free": True,
        },
        {
            "id": "deepseek/deepseek-r1-distill-qwen-14b:free",
            "name": "DeepSeek R1 Distill 14B (Free)",
            "description": "Modelo eficiente de DeepSeek con conocimiento destilado",
            "context_length": 32000,
            "multimodal": False,
            "free": True,
        },
        {
            "id": "mistralai/mistral-small-3.1-24b-instruct:free",
            "name": "Mistral Small 3.1 24B (Free)",
            "description": "Modelo de Mistral AI optimizado para instrucciones",
            "context_length": 32000,
            "multimodal": False,
            "free": True,
        },
    ]

    try:
        # Intentar obtener la API key de OpenRouter
        api_key = None
        if hasattr(st, "secrets") and "OPENROUTER_API_KEY" in st.secrets:
            api_key = st.secrets["OPENROUTER_API_KEY"]
        elif os.environ.get("OPENROUTER_API_KEY"):
            api_key = os.environ.get("OPENROUTER_API_KEY")

        if not api_key:
            return default_models  # Devolver modelos por defecto si no hay API key

        # Hacer la solicitud a la API de OpenRouter
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        response = requests.get("https://openrouter.ai/api/v1/models", headers=headers)

        if response.status_code == 200:
            models_data = response.json()

            # Filtrar SOLO modelos multimodales GRATUITOS o con "free" en su nombre/descripción
            free_multimodal_models = []
            for model in models_data.get("data", []):
                context_length = model.get("context_length", 0)
                pricing = model.get("pricing", {})
                model_name = model.get("name", "").lower()
                model_description = model.get("description", "").lower()
                model_id = model.get("id", "").lower()

                # Verificar si es gratuito según pricing
                is_free_pricing = (
                    pricing.get("prompt", 1) == 0 and pricing.get("completion", 1) == 0
                )

                # Verificar si tiene "free" en el nombre, descripción o ID
                has_free_in_name = "free" in model_name
                has_free_in_description = "free" in model_description
                has_free_in_id = "free" in model_id

                is_multimodal = model.get("multimodal", False)

                # Determinar si el modelo es realmente gratuito
                is_truly_free = (
                    is_free_pricing
                    or has_free_in_name
                    or has_free_in_description
                    or has_free_in_id
                )

                # Excluir modelos que tienen "not free" o "paid" en su descripción
                has_not_free = (
                    "not free" in model_description or "paid" in model_description
                )

                # Incluir SOLO si es multimodal Y es realmente gratuito Y no tiene indicaciones de que no es gratuito
                if is_multimodal and is_truly_free and not has_not_free:
                    free_multimodal_models.append(
                        {
                            "id": model.get("id"),
                            "name": model.get("name"),
                            "description": model.get("description"),
                            "context_length": context_length,
                            "multimodal": True,
                        }
                    )

            # Si no encontramos modelos gratuitos, devolver los modelos por defecto
            if not free_multimodal_models:
                return default_models

            return free_multimodal_models
        else:
            st.warning(
                f"Error al obtener modelos de OpenRouter: {response.status_code}"
            )
            return default_models  # Devolver modelos por defecto en caso de error
    except Exception as e:
        st.warning(f"Error al conectar con OpenRouter: {str(e)}")
        return default_models  # Devolver modelos por defecto en caso de excepción


def configure_openrouter_client(multimodal_only=False):
    """
    Configura un cliente para OpenRouter con manejo de errores y recuperación

    Args:
        multimodal_only (bool): Si es True, solo muestra modelos multimodales

    Returns:
        tuple: (api_key, model_id)
    """
    # Intentar obtener la API key de OpenRouter
    api_key = None
    if hasattr(st, "secrets") and "OPENROUTER_API_KEY" in st.secrets:
        api_key = st.secrets["OPENROUTER_API_KEY"]

    # Si no está en secrets, solicitar al usuario
    if not api_key:
        api_key = st.sidebar.text_input(
            label="OpenRouter API Key",
            type="password",
            placeholder="sk-or-...",
            key="OPENROUTER_API_KEY",
            help="Obtén tu clave API en https://openrouter.ai/keys",
        )

    if not api_key:
        st.error("Por favor, añade tu clave API de OpenRouter para continuar.")
        st.info("Obtén tu clave en: https://openrouter.ai/keys")
        st.stop()

    # Obtener modelos disponibles (siempre devuelve al menos los modelos por defecto)
    free_models = get_openrouter_free_models()

    # Si se solicitan solo modelos multimodales, filtrarlos
    if multimodal_only:
        multimodal_models = [
            model for model in free_models if model.get("multimodal", False)
        ]

        # Si no hay modelos multimodales, mostrar un mensaje pero usar los modelos disponibles
        if not multimodal_models:
            st.info(
                "No se encontraron modelos multimodales gratuitos. Usando modelos de texto gratuitos disponibles."
            )
            available_models = free_models
        else:
            available_models = multimodal_models
            st.success(
                f"Se encontraron {len(multimodal_models)} modelos multimodales gratuitos."
            )
    else:
        # Usar todos los modelos gratuitos disponibles
        available_models = free_models
        # Contar cuántos son multimodales para informar al usuario
        multimodal_count = sum(
            1 for model in free_models if model.get("multimodal", False)
        )
        if multimodal_count > 0:
            st.info(
                f"{multimodal_count} de los {len(free_models)} modelos gratuitos disponibles son multimodales (indicados con 🖼️)."
            )

    # Crear opciones para el selector (solo modelos gratuitos)
    model_options = {}
    for model in available_models:
        # Añadir indicador de multimodal y gratuito al nombre para mejor claridad
        name = model["name"]
        if model.get("multimodal", False):
            name += " 🖼️"
        if "free" not in name.lower():
            name += " (Free)"  # Añadir (Free) si no está ya en el nombre
        model_options[name] = model["id"]

    # Mostrar mensaje informativo sobre modelos gratuitos
    st.sidebar.info(
        """
    **Nota:** Solo se muestran modelos gratuitos o con versión gratuita.
    Los modelos con 🖼️ soportan imágenes.
    """
    )

    # Mostrar selector de modelos con manejo de errores
    try:
        selected_name = st.sidebar.selectbox(
            "Modelo Gratuito de OpenRouter",
            options=list(model_options.keys()),
            key="SELECTED_OPENROUTER_MODEL",
            help="Selecciona un modelo gratuito. Los modelos con 🖼️ soportan imágenes.",
        )
        model_id = model_options.get(selected_name)
    except Exception as e:
        # En caso de error, usar el primer modelo disponible
        st.warning(f"Error al seleccionar modelo: {str(e)}. Usando modelo por defecto.")
        model_id = available_models[0]["id"]

    # Mostrar información sobre el modelo seleccionado
    selected_model = next((m for m in available_models if m["id"] == model_id), None)
    if selected_model:
        with st.sidebar.expander("Información del modelo"):
            st.write(f"**ID:** {selected_model['id']}")
            st.write(
                f"**Descripción:** {selected_model.get('description', 'No disponible')}"
            )
            st.write(
                f"**Longitud de contexto:** {selected_model.get('context_length', 'No disponible')}"
            )
            st.write(
                f"**Multimodal:** {'Sí' if selected_model.get('multimodal', False) else 'No'}"
            )

    return api_key, model_id


def get_mistral_api_key():
    """
    Obtiene la clave API de Mistral

    Returns:
        str: Clave API de Mistral
    """
    # Intentar obtener la API key de Mistral
    api_key = None
    if hasattr(st, "secrets") and "MISTRAL_API_KEY" in st.secrets:
        api_key = st.secrets["MISTRAL_API_KEY"]
    elif os.environ.get("MISTRAL_API_KEY"):
        api_key = os.environ.get("MISTRAL_API_KEY")

    # Si no está en secrets ni en variables de entorno, solicitar al usuario
    if not api_key:
        api_key = st.sidebar.text_input(
            label="Mistral API Key",
            type="password",
            placeholder="...",
            key="MISTRAL_API_KEY",
            help="Obtén tu clave API en https://console.mistral.ai/api-keys/",
        )

    return api_key

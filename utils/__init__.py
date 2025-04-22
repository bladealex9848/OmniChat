"""Módulo de utilidades para OmniChat.
Detecta automáticamente si estamos en Streamlit Cloud o en local."""

import os
import sys
import importlib.util

# Importar funciones comunes
from .chat_utils import enable_chat_history, display_msg, sync_st_session
from .page_utils import setup_page

# Detectar si estamos en Streamlit Cloud
is_streamlit_cloud = os.environ.get('IS_STREAMLIT_CLOUD') == 'true'

# Importar la versión correcta de las utilidades de LLM
try:
    if is_streamlit_cloud:
        # Versión para Streamlit Cloud
        from .llm_utils_cloud import (
            configure_llm,
            configure_openrouter_client,
            get_mistral_api_key,
        )
    else:
        # Versión local
        from .llm_utils import (
            configure_llm,
            configure_openrouter_client,
            get_mistral_api_key,
        )
except ImportError:
    # Si no existe llm_utils_cloud.py, usar llm_utils.py
    from .llm_utils import (
        configure_llm,
        configure_openrouter_client,
        get_mistral_api_key,
    )

# Intentar importar langchain_huggingface para evitar errores
try:
    import langchain_huggingface
except ImportError:
    print("ADVERTENCIA: No se pudo importar langchain_huggingface. Algunas funcionalidades pueden no estar disponibles.")

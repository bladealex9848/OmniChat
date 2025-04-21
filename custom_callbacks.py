"""
Callbacks personalizados para ocultar la cadena de pensamiento en el chat.
"""

from typing import Any, Dict, List, Optional, Union
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.outputs import LLMResult
import streamlit as st


class CustomStreamlitCallbackHandler(BaseCallbackHandler):
    """
    Callback handler personalizado para Streamlit que oculta la cadena de pensamiento.
    Solo muestra la respuesta final, no los pasos intermedios.
    """

    def __init__(self, container: Optional[Any] = None):
        """
        Inicializa el callback handler.

        Args:
            container: Contenedor de Streamlit donde mostrar la salida.
        """
        self.container = container or st.container()
        self._current_thought = ""
        self.thoughts = []
        self.show_intermediate = False  # Por defecto, no mostrar pasos intermedios

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Método llamado cuando el LLM comienza a generar."""
        pass

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Método llamado cuando el LLM genera un nuevo token."""
        pass

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Método llamado cuando el LLM termina de generar."""
        pass

    def on_llm_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """Método llamado cuando el LLM encuentra un error."""
        pass

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        """Método llamado cuando una cadena comienza a ejecutarse."""
        pass

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Método llamado cuando una cadena termina de ejecutarse."""
        pass

    def on_chain_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """Método llamado cuando una cadena encuentra un error."""
        pass

    def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> None:
        """Método llamado cuando una herramienta comienza a ejecutarse."""
        # No mostramos nada cuando la herramienta comienza
        pass

    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """Método llamado cuando una herramienta termina de ejecutarse."""
        # Guardar el resultado en la lista de pensamientos
        thought = f"Resultado: {output}\n"
        self.thoughts.append(thought)

        # Si se ha activado la visualización de pasos intermedios, mostrar el resultado
        if self.show_intermediate:
            with self.container:
                st.markdown(f"**Resultado:** {output}")

    def on_tool_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """Método llamado cuando una herramienta encuentra un error."""
        # No mostramos errores de herramientas
        pass

    def on_text(self, text: str, **kwargs: Any) -> None:
        """Método llamado cuando se genera texto."""
        # No mostramos nada para ocultar la cadena de pensamiento
        # La respuesta final se mostrará directamente en la interfaz principal
        pass

    def on_agent_action(self, action: Dict[str, Any], **kwargs: Any) -> Any:
        """Método llamado cuando un agente toma una acción."""
        # Guardar la acción en la lista de pensamientos
        thought = f"Acción: {action.get('tool', 'Desconocida')}\nEntrada: {action.get('tool_input', '')}\n"
        self.thoughts.append(thought)

        # Si se ha activado la visualización de pasos intermedios, mostrar la acción
        if self.show_intermediate:
            with self.container:
                st.markdown(f"**Acción:** {action.get('tool', 'Desconocida')}")
                st.markdown(f"**Entrada:** {action.get('tool_input', '')}")

    def on_agent_finish(self, finish: Dict[str, Any], **kwargs: Any) -> None:
        """Método llamado cuando un agente termina."""
        # Obtener la respuesta final
        output = finish.get("output", "No se encontró una respuesta.")

        # Guardar la respuesta final en la lista de pensamientos
        thought = f"Respuesta final: {output}\n"
        self.thoughts.append(thought)

        # No mostramos la respuesta aquí, se mostrará a través del historial de mensajes
        # La respuesta se añade al historial en pages/3_🌐_Chatbot_Acceso_Internet.py

        # Añadir un botón para mostrar/ocultar la cadena de pensamiento
        if self.thoughts:
            with self.container:
                if st.button("Mostrar cadena de pensamiento", key="show_thoughts"):
                    st.markdown("### Cadena de pensamiento:")
                    for t in self.thoughts:
                        st.markdown(f"```\n{t}\n```")

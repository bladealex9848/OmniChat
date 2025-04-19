import os
import sys

# Añadir el directorio raíz al path para poder importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils
import streamlit as st
from streaming import StreamHandler
from PIL import Image
from io import BytesIO
import base64
import openai

st.set_page_config(page_title="Chat Multimodal Gratuito", page_icon="🖼️")
st.title("Chat Multimodal con Modelos Gratuitos")
st.write(
    """
    Permite al chatbot analizar imágenes y responder preguntas sobre ellas usando **exclusivamente modelos multimodales gratuitos** de OpenRouter.

    > **Nota:** En esta página solo se muestran modelos multimodales gratuitos o que tengan "free" en su nombre.
    > En otras páginas de la aplicación podrás ver todos los modelos gratuitos disponibles.
    """
)

# Mostrar información sobre los modelos disponibles
with st.expander("Ver modelos multimodales gratuitos disponibles"):
    st.markdown(
        """
    ### Modelos multimodales gratuitos disponibles

    Esta aplicación utiliza una amplia variedad de modelos multimodales gratuitos, incluyendo:

    - **Meta Llama 4 Maverick/Scout**: Modelos multimodales de Meta con capacidades avanzadas de visión y razonamiento.
    - **Qwen 2.5 VL**: Modelos multimodales de Qwen con soporte para visión y múltiples idiomas.
    - **Google Gemini**: Modelos de Google con capacidades multimodales y razonamiento avanzado.
    - **Claude 3 Haiku**: Modelo multimodal rápido y eficiente de Anthropic.
    - **GPT-4o Mini**: Versión gratuita del modelo multimodal de OpenAI.

    Todos estos modelos son completamente gratuitos para usar y no requieren pago alguno.
    """
    )

    st.info(
        "Los modelos disponibles pueden variar según la disponibilidad en OpenRouter. La aplicación siempre seleccionará automáticamente modelos gratuitos."
    )


class MultimodalChatbot:
    def __init__(self):
        utils.sync_st_session()
        self.setup_openrouter_client()

    def setup_openrouter_client(self):
        """Configura el cliente de OpenRouter para chat multimodal con manejo de errores"""
        try:
            # Obtener API key y modelo de OpenRouter (solo modelos multimodales)
            self.api_key, self.model_id = utils.configure_openrouter_client(
                multimodal_only=True
            )

            # Verificar si el modelo seleccionado es multimodal
            if not self._is_model_multimodal(self.model_id):
                st.sidebar.warning(
                    f"El modelo seleccionado ({self.model_id}) puede no ser multimodal. "
                    "Las imágenes podrían no procesarse correctamente."
                )
                st.sidebar.info(
                    "Recomendación: Selecciona un modelo con el icono 🖼️ que indica soporte para imágenes."
                )

            # Crear cliente de OpenAI pero con la base_url de OpenRouter
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url="https://openrouter.ai/api/v1",
                default_headers={
                    "HTTP-Referer": "https://github.com/bladealex9848/OmniChat",
                    "X-Title": "OmniChat",
                },
            )
        except Exception as e:
            st.error(f"Error al configurar OpenRouter: {str(e)}")
            st.info("Usando configuración alternativa con modelo por defecto.")

            # Configuración de respaldo
            if hasattr(st, "secrets") and "OPENROUTER_API_KEY" in st.secrets:
                self.api_key = st.secrets["OPENROUTER_API_KEY"]
            else:
                self.api_key = "DEMO"  # OpenRouter permite algunas llamadas con DEMO

            self.model_id = "anthropic/claude-3-haiku:beta"  # Modelo por defecto

            # Crear cliente con configuración de respaldo
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url="https://openrouter.ai/api/v1",
                default_headers={
                    "HTTP-Referer": "https://github.com/bladealex9848/OmniChat",
                    "X-Title": "OmniChat",
                },
            )

    def _is_model_multimodal(self, model_id):
        """Verifica si un modelo es multimodal basándose en su ID o en la lista de modelos conocidos"""
        # Lista de modelos conocidos por ser multimodales
        known_multimodal_models = [
            # Modelos de Anthropic
            "anthropic/claude-3-haiku",
            "anthropic/claude-3-opus",
            "anthropic/claude-3-sonnet",
            # Modelos de Google
            "google/gemini-pro-vision",
            "google/gemini-2.5-pro",
            # Modelos de OpenAI
            "openai/gpt-4-vision",
            "openai/gpt-4o",
            # Modelos de Meta
            "meta-llama/llama-4-maverick",
            "meta-llama/llama-4-scout",
            # Modelos de Qwen
            "qwen/qwen2.5-vl",
            # Otros modelos multimodales
            "mistralai/mistral-large-vision",
            "cohere/command-r-vision",
        ]

        # Verificar si el ID del modelo contiene alguno de los modelos conocidos
        for known_model in known_multimodal_models:
            if known_model in model_id.lower():
                return True

        # Verificar si el modelo tiene palabras clave que indican capacidad multimodal
        multimodal_keywords = [
            "vision",
            "image",
            "visual",
            "multimodal",
            "vl",
            "img",
            "picture",
            "photo",
            "camera",
            "sight",
            "see",
            "view",
        ]
        for keyword in multimodal_keywords:
            if keyword in model_id.lower():
                return True

        # Por defecto, asumir que no es multimodal si no podemos confirmarlo
        return False

    def encode_image_to_base64(self, image_file):
        """Convierte una imagen a base64 para enviarla a la API"""
        return base64.b64encode(image_file.getvalue()).decode("utf-8")

    def process_image_with_openrouter(self, image_file, prompt):
        """Procesa una imagen con OpenRouter usando el modelo multimodal seleccionado"""
        try:
            # Codificar imagen en base64
            base64_image = self.encode_image_to_base64(image_file)

            # Crear mensaje con la imagen
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ]

            # Mostrar indicador de procesamiento
            with st.status("Procesando imagen...", expanded=False) as status:
                # Llamar a la API de OpenRouter
                response = self.client.chat.completions.create(
                    model=self.model_id, messages=messages, max_tokens=1000, stream=True
                )
                status.update(label="¡Imagen procesada!", state="complete")
                return response

        except openai.BadRequestError as e:
            # Error específico de formato o capacidad del modelo
            error_msg = str(e)
            if "multimodal" in error_msg.lower() or "image" in error_msg.lower():
                st.error("El modelo seleccionado no soporta procesamiento de imágenes.")
                st.info("Intentando con un modelo alternativo...")

                # Intentar con un modelo alternativo conocido por ser multimodal
                try:
                    backup_model = "anthropic/claude-3-haiku:beta"
                    st.info(f"Usando modelo de respaldo: {backup_model}")

                    response = self.client.chat.completions.create(
                        model=backup_model,
                        messages=messages,
                        max_tokens=1000,
                        stream=True,
                    )
                    return response
                except Exception as backup_error:
                    st.error(f"Error con el modelo de respaldo: {str(backup_error)}")
            else:
                st.error(f"Error en la solicitud: {error_msg}")

            # Proporcionar una respuesta alternativa
            return self._generate_fallback_response(prompt, image_file)

        except openai.RateLimitError:
            st.warning(
                "Se ha alcanzado el límite de solicitudes. Intentando con un modelo alternativo..."
            )
            # Intentar con un modelo alternativo o proporcionar una respuesta alternativa
            return self._generate_fallback_response(prompt, image_file)

        except Exception as e:
            st.error(f"Error al procesar la imagen: {str(e)}")
            # Proporcionar una respuesta alternativa
            return self._generate_fallback_response(prompt, image_file)

    def _generate_fallback_response(self, prompt, image_file):
        """Genera una respuesta alternativa cuando falla el procesamiento de la imagen"""
        try:
            # Crear una respuesta simulada para no interrumpir la experiencia del usuario
            class FallbackResponse:
                def __init__(self, prompt):
                    self.prompt = prompt
                    self.choices = [self.Choice()]

                class Choice:
                    def __init__(self):
                        self.delta = self.Delta()

                    class Delta:
                        def __init__(self):
                            self.content = None

            # Crear un generador que simule la respuesta streaming
            def fallback_generator():
                # Mensaje inicial
                response = FallbackResponse(prompt)
                response.choices[0].delta.content = (
                    "Lo siento, no puedo procesar esta imagen en este momento. "
                )
                yield response

                # Mensaje de explicación
                response = FallbackResponse(prompt)
                response.choices[0].delta.content = (
                    "Estoy experimentando dificultades técnicas con el servicio de procesamiento de imágenes. "
                )
                yield response

                # Sugerencia basada en el prompt
                response = FallbackResponse(prompt)
                if "describe" in prompt.lower():
                    response.choices[0].delta.content = (
                        "Para describir mejor la imagen, por favor intenta con un modelo diferente o proporciona más detalles sobre lo que estás viendo. "
                    )
                elif "analiza" in prompt.lower() or "analizar" in prompt.lower():
                    response.choices[0].delta.content = (
                        "Para analizar la imagen, necesitaría poder procesarla correctamente. Por favor, intenta con un modelo diferente. "
                    )
                else:
                    response.choices[0].delta.content = (
                        "Para responder a tu pregunta sobre la imagen, necesitaría poder procesarla correctamente. "
                    )
                yield response

                # Mensaje final
                response = FallbackResponse(prompt)
                response.choices[0].delta.content = (
                    "Te recomiendo seleccionar un modelo con el icono 🖼️ que indica soporte para imágenes."
                )
                yield response

            return fallback_generator()

        except Exception as e:
            # Si todo falla, devolver None y dejar que el código principal maneje el error
            st.error(f"Error al generar respuesta alternativa: {str(e)}")
            return None

    @utils.enable_chat_history
    def main(self):
        # Área para cargar imágenes
        uploaded_file = st.sidebar.file_uploader(
            "Sube una imagen para analizar",
            type=["jpg", "jpeg", "png"],
            help="Sube una imagen para que el modelo la analice",
        )

        # Mostrar la imagen si se ha cargado
        if uploaded_file:
            st.sidebar.image(
                uploaded_file, caption="Imagen cargada", use_container_width=True
            )

            # Guardar la imagen en la sesión
            if "current_image" not in st.session_state:
                st.session_state.current_image = uploaded_file
                st.rerun()  # Recargar para actualizar la interfaz

        # Entrada de chat
        user_query = st.chat_input(
            placeholder="Hazme una pregunta sobre la imagen o sube una nueva imagen",
            accept_file=True,
            file_type=["jpg", "jpeg", "png"],
        )

        # Procesar entrada del usuario
        if user_query:
            # Verificar si hay texto o archivos
            user_text = ""
            user_files = []

            if hasattr(user_query, "text"):
                user_text = user_query.text

            if hasattr(user_query, "files") and user_query.files:
                user_files = user_query.files
            elif (
                isinstance(user_query, dict)
                and "files" in user_query
                and user_query["files"]
            ):
                user_files = user_query["files"]

            # Si hay archivos, actualizar la imagen actual
            if user_files:
                image_file = user_files[0]
                st.session_state.current_image = image_file

                # Mostrar mensaje de carga de imagen
                display_message = f"*He cargado una nueva imagen para análisis*"
                if user_text:
                    display_message = f"{user_text}\n\n{display_message}"

                utils.display_msg(display_message, "user")
                st.sidebar.image(
                    image_file, caption="Imagen cargada", use_container_width=True
                )

                # Si no hay texto, usar un prompt predeterminado
                if not user_text:
                    user_text = "Describe detalladamente esta imagen."
            else:
                # Si solo hay texto, mostrar el mensaje del usuario
                utils.display_msg(user_text, "user")

            # Verificar que haya una imagen para analizar
            if (
                "current_image" not in st.session_state
                or not st.session_state.current_image
            ):
                st.error("Por favor, sube una imagen para analizar primero.")
                return

            # Procesar la imagen con el modelo multimodal
            with st.chat_message("assistant"):
                st_cb = StreamHandler(st.empty())

                # Obtener respuesta del modelo
                response_stream = self.process_image_with_openrouter(
                    st.session_state.current_image, user_text
                )

                if response_stream:
                    full_response = ""
                    for chunk in response_stream:
                        if chunk.choices[0].delta.content:
                            content = chunk.choices[0].delta.content
                            full_response += content
                            st_cb.text = full_response
                            st_cb.container.markdown(st_cb.text)

                    # Guardar la respuesta en el historial
                    st.session_state.messages.append(
                        {"role": "assistant", "content": full_response}
                    )
                else:
                    st.error(
                        "No se pudo obtener una respuesta del modelo. Por favor, intenta de nuevo."
                    )


if __name__ == "__main__":
    obj = MultimodalChatbot()
    obj.main()

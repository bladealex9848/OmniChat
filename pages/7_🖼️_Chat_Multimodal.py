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

st.set_page_config(page_title="Chat Multimodal", page_icon="🖼️")
st.title("Chat Multimodal con OpenRouter")
st.write(
    "Permite al chatbot analizar imágenes y responder preguntas sobre ellas usando modelos multimodales gratuitos de OpenRouter."
)


class MultimodalChatbot:
    def __init__(self):
        utils.sync_st_session()
        self.setup_openrouter_client()

    def setup_openrouter_client(self):
        """Configura el cliente de OpenRouter para chat multimodal"""
        # Obtener API key y modelo de OpenRouter
        self.api_key, self.model_id = utils.configure_openrouter_client()

        # Crear cliente de OpenAI pero con la base_url de OpenRouter
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://github.com/bladealex9848/OmniChat",
                "X-Title": "OmniChat",
            },
        )

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

            # Llamar a la API de OpenRouter
            response = self.client.chat.completions.create(
                model=self.model_id, messages=messages, max_tokens=1000, stream=True
            )

            return response

        except Exception as e:
            st.error(f"Error al procesar la imagen: {str(e)}")
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
                uploaded_file, caption="Imagen cargada", use_column_width=True
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
                    image_file, caption="Imagen cargada", use_column_width=True
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

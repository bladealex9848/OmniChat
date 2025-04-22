import os
import sys
import base64
import json
import time
import logging
from io import BytesIO
from typing import Dict, List, Any, Optional, Tuple

# Añadir el directorio raíz al path para poder importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils
import streamlit as st
from streaming import StreamHandler
from PIL import Image

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Configuración de la página (debe ser la primera llamada a Streamlit)
st.set_page_config(page_title="ChatMultimodal", page_icon="🖼️")

# Inicializar mensajes si no existen
if "multimodal_chat_messages" not in st.session_state:
    st.session_state["multimodal_chat_messages"] = [
        {
            "role": "assistant",
            "content": "Hola, soy un asistente virtual. ¿En qué puedo ayudarte hoy?",
        }
    ]

class MultimodalChatbot:
    def __init__(self):
        utils.sync_st_session()
        self.llm = None
        self.image_data = None
        self.image_base64 = None

    def encode_image(self, image_file):
        """Codifica una imagen a base64 para enviarla a la API."""
        if image_file is None:
            return None
        
        try:
            # Leer el archivo de imagen
            image_data = image_file.getvalue()
            
            # Codificar a base64
            base64_image = base64.b64encode(image_data).decode("utf-8")
            
            return base64_image
        except Exception as e:
            st.error(f"Error al codificar la imagen: {str(e)}")
            return None

    def resize_image(self, image_file, max_size=(1024, 1024)):
        """Redimensiona una imagen si es demasiado grande."""
        if image_file is None:
            return None
        
        try:
            # Abrir la imagen con PIL
            image = Image.open(BytesIO(image_file.getvalue()))
            
            # Verificar si la imagen necesita ser redimensionada
            if image.width > max_size[0] or image.height > max_size[1]:
                # Calcular la relación de aspecto
                aspect_ratio = image.width / image.height
                
                # Determinar nuevas dimensiones manteniendo la relación de aspecto
                if image.width > image.height:
                    new_width = max_size[0]
                    new_height = int(new_width / aspect_ratio)
                else:
                    new_height = max_size[1]
                    new_width = int(new_height * aspect_ratio)
                
                # Redimensionar la imagen
                image = image.resize((new_width, new_height), Image.LANCZOS)
                
                # Convertir la imagen redimensionada a bytes
                buffer = BytesIO()
                image.save(buffer, format=image.format if image.format else "JPEG")
                buffer.seek(0)
                
                return buffer.getvalue()
            else:
                # Si la imagen ya es lo suficientemente pequeña, devolver los bytes originales
                return image_file.getvalue()
        except Exception as e:
            st.error(f"Error al redimensionar la imagen: {str(e)}")
            return image_file.getvalue()

    def process_image(self, image_file):
        """Procesa una imagen para su uso con modelos multimodales."""
        if image_file is None:
            return None, None
        
        try:
            # Redimensionar la imagen si es necesario
            image_data = self.resize_image(image_file)
            
            # Codificar a base64
            base64_image = base64.b64encode(image_data).decode("utf-8")
            
            return image_data, base64_image
        except Exception as e:
            st.error(f"Error al procesar la imagen: {str(e)}")
            return None, None

    def get_multimodal_response(self, prompt, image_base64=None):
        """Obtiene una respuesta del modelo multimodal."""
        try:
            # Verificar si tenemos una imagen
            if image_base64:
                # Usar OpenRouter para modelos multimodales
                from utils.llm_utils import configure_openrouter_client
                
                # Configurar cliente de OpenRouter específicamente para modelos multimodales
                client = configure_openrouter_client(multimodal_only=True, key_suffix="_multimodal")
                
                if client is None:
                    st.error("No se pudo configurar el cliente de OpenRouter para modelos multimodales.")
                    return "Lo siento, no se pudo configurar el modelo multimodal. Por favor, verifica tu clave API de OpenRouter."
                
                # Preparar los mensajes para la API
                messages = [
                    {"role": "system", "content": "Eres un asistente útil que puede analizar imágenes y responder preguntas sobre ellas."},
                    {"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]}
                ]
                
                # Realizar la solicitud a la API
                response = client.chat.completions.create(
                    messages=messages,
                    stream=True
                )
                
                return response
            else:
                # Si no hay imagen, usar el LLM normal
                return self.llm.invoke(prompt, streaming=True)
        except Exception as e:
            logger.error(f"Error al obtener respuesta multimodal: {str(e)}")
            st.error(f"Error al obtener respuesta multimodal: {str(e)}")
            return f"Lo siento, ocurrió un error al procesar tu solicitud: {str(e)}"

    def main(self):
        # 1. Título y subtítulo (siempre visible en la parte superior)
        st.title("Chat Multimodal con Imágenes")
        st.write("Permite al chatbot analizar imágenes y responder preguntas sobre ellas.")
        
        # Primero configurar el LLM en la barra lateral
        st.sidebar.markdown("### 🤖 Selecciona el modelo")
        self.llm = utils.configure_llm(key_suffix="_sidebar")
        
        # Luego mostrar instrucciones específicas para el chatbot multimodal
        with st.sidebar.expander("🖼️ Instrucciones de uso", expanded=True):
            st.markdown("""
            ### Cómo usar el Chat Multimodal
            
            1. **Sube una imagen** usando el selector de archivos en la barra lateral
            2. **Haz preguntas** sobre la imagen subida
            3. **Interactúa** con el asistente para obtener más detalles
            
            #### Funcionalidades
            - Análisis de imágenes (fotos, diagramas, capturas de pantalla)
            - Descripción detallada del contenido visual
            - Respuestas a preguntas específicas sobre la imagen
            
            #### Consejos
            - Usa imágenes claras y de buena calidad
            - Haz preguntas específicas sobre elementos de la imagen
            - Puedes subir una nueva imagen en cualquier momento
            """)
        
        # Área para cargar imágenes
        uploaded_file = st.sidebar.file_uploader(
            "Sube una imagen para analizar",
            type=["jpg", "jpeg", "png"],
            help="Sube una imagen para que el modelo la analice",
        )
        
        # Mostrar información del autor en la barra lateral (al final)
        try:
            from sidebar_info import show_author_info
            show_author_info()
        except ImportError:
            st.sidebar.warning("No se pudo cargar la información del autor.")
        
        # Procesar la imagen si se ha subido una
        if uploaded_file:
            # Mostrar la imagen en la barra lateral
            st.sidebar.image(uploaded_file, caption="Imagen cargada", use_column_width=True)
            
            # Procesar la imagen
            self.image_data, self.image_base64 = self.process_image(uploaded_file)
            
            if self.image_base64 is None:
                st.error("No se pudo procesar la imagen. Por favor, intenta con otra imagen.")
                st.stop()
        else:
            st.info("👆 Por favor, sube una imagen en la barra lateral para comenzar.")
            st.stop()
        
        # 2. Mostrar mensajes del historial (saludo inicial y conversación)
        for msg in st.session_state["multimodal_chat_messages"]:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
        
        # 3. Campo de entrada para nuevas preguntas (al final)
        user_query = st.chat_input(
            placeholder="¡Hazme una pregunta sobre la imagen!"
        )
        
        if user_query and self.image_base64:
            # Añadir mensaje del usuario al historial
            st.session_state["multimodal_chat_messages"].append({"role": "user", "content": user_query})
            
            # Mostrar mensaje del usuario (se mostrará en la próxima ejecución)
            with st.chat_message("user"):
                st.write(user_query)
            
            # Crear un contenedor para mostrar el estado del procesamiento
            processing_container = st.container()
            
            # Mostrar un mensaje de procesamiento
            with processing_container:
                status_text = st.empty()
                status_text.text("Analizando imagen y preparando respuesta...")
            
            # Generar respuesta
            with st.chat_message("assistant"):
                # Procesar la consulta en un contenedor oculto
                with st.container():
                    # Crear un elemento vacío que no se mostrará al usuario
                    hidden_element = st.empty()
                    # Usar el StreamHandler con el elemento oculto
                    st_cb = StreamHandler(hidden_element)
                    # Invocar el modelo multimodal
                    response_stream = self.get_multimodal_response(user_query, self.image_base64)
                    
                    # Procesar la respuesta según si es streaming o no
                    if hasattr(response_stream, "__iter__"):
                        # Es un objeto de streaming
                        response_text = ""
                        for chunk in response_stream:
                            if hasattr(chunk, "choices") and len(chunk.choices) > 0:
                                content = chunk.choices[0].delta.content
                                if content:
                                    response_text += content
                                    hidden_element.markdown(response_text)
                    else:
                        # No es streaming, es una respuesta directa
                        response_text = response_stream
                        hidden_element.markdown(response_text)
                    
                    # Limpiar el elemento oculto
                    hidden_element.empty()
                
                # Mostrar la respuesta una sola vez
                st.write(response_text)
                
                # Añadir respuesta al historial
                st.session_state["multimodal_chat_messages"].append(
                    {"role": "assistant", "content": response_text}
                )
            
            # Limpiar el contenedor de procesamiento
            processing_container.empty()


if __name__ == "__main__":
    obj = MultimodalChatbot()
    obj.main()

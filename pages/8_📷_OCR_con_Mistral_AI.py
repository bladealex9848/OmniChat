import os
import sys
import io
import base64
from typing import List, Dict, Any, Optional
from PIL import Image

# Añadir el directorio raíz al path para poder importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils
import streamlit as st
from streaming import StreamHandler

# Configuración de la página (debe ser la primera llamada a Streamlit)
st.set_page_config(page_title="OCR con Mistral AI", page_icon="📷")

# Inicializar mensajes si no existen
if "ocr_messages" not in st.session_state:
    st.session_state["ocr_messages"] = [
        {
            "role": "assistant",
            "content": "Hola, soy un asistente de OCR. Puedo extraer texto de imágenes y documentos PDF. Sube un archivo para comenzar.",
        }
    ]

class MistralOCRApp:
    def __init__(self):
        utils.sync_st_session()
        self.llm = None
        self.mistral_api_key = None
        self.max_file_size = 5 * 1024 * 1024  # 5 MB en bytes

    def get_image_base64(self, image):
        """Convierte una imagen PIL a base64"""
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return img_str

    def process_image_with_mistral(self, image, prompt="Extrae todo el texto visible en esta imagen."):
        """Procesa una imagen con la API de Mistral AI para OCR"""
        import mistralai.client
        from mistralai.client import MistralClient
        from mistralai.models.chat_completion import ChatMessage

        # Convertir imagen a base64
        base64_image = self.get_image_base64(image)

        # Crear cliente de Mistral
        client = MistralClient(api_key=self.mistral_api_key)

        # Crear mensaje con la imagen
        messages = [
            ChatMessage(role="user", content=[
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64_image}"
                    }
                }
            ])
        ]

        # Llamar a la API de Mistral
        try:
            chat_response = client.chat(
                model="mistral-large-latest",
                messages=messages,
            )
            return chat_response.choices[0].message.content
        except Exception as e:
            st.error(f"Error al procesar la imagen con Mistral AI: {str(e)}")
            return None

    def process_pdf_with_mistral(self, pdf_file, prompt="Extrae todo el texto visible en este documento."):
        """Procesa un PDF con la API de Mistral AI para OCR"""
        import fitz  # PyMuPDF
        
        try:
            # Abrir el PDF
            pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
            
            # Procesar cada página
            all_text = ""
            
            # Limitar a las primeras 5 páginas para evitar exceder límites de API
            max_pages = min(5, len(pdf_document))
            
            for page_num in range(max_pages):
                with st.spinner(f"Procesando página {page_num + 1} de {max_pages}..."):
                    page = pdf_document[page_num]
                    
                    # Renderizar página como imagen
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Escala 2x para mejor calidad
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    
                    # Procesar imagen con Mistral
                    page_text = self.process_image_with_mistral(
                        img, 
                        f"Extrae todo el texto visible en esta página {page_num + 1} del documento PDF."
                    )
                    
                    if page_text:
                        all_text += f"\n--- PÁGINA {page_num + 1} ---\n{page_text}\n"
            
            return all_text if all_text else "No se pudo extraer texto del PDF."
            
        except Exception as e:
            st.error(f"Error al procesar el PDF: {str(e)}")
            return None

    def display_file_uploader(self):
        """Muestra el selector de archivos"""
        uploaded_file = st.file_uploader(
            "Sube una imagen o PDF para extraer texto",
            type=["jpg", "jpeg", "png", "pdf"],
            key="ocr_file_uploader",
            help="Formatos soportados: JPG, JPEG, PNG, PDF. Tamaño máximo: 5 MB."
        )
        
        if uploaded_file is not None:
            # Verificar tamaño del archivo
            if uploaded_file.size > self.max_file_size:
                st.error(f"El archivo es demasiado grande. El tamaño máximo permitido es 5 MB.")
                return None
            
            # Mostrar vista previa
            file_type = uploaded_file.type
            if file_type.startswith("image"):
                st.image(uploaded_file, caption="Vista previa de la imagen", use_column_width=True)
                return {"type": "image", "file": uploaded_file}
            elif file_type == "application/pdf":
                st.info(f"PDF cargado: {uploaded_file.name}")
                return {"type": "pdf", "file": uploaded_file}
        
        return None

    def process_file(self, file_info, prompt=None):
        """Procesa el archivo según su tipo"""
        if not file_info:
            return None
        
        with st.spinner("Procesando archivo..."):
            if file_info["type"] == "image":
                # Procesar imagen
                image = Image.open(file_info["file"])
                custom_prompt = prompt if prompt else "Extrae todo el texto visible en esta imagen."
                return self.process_image_with_mistral(image, custom_prompt)
            
            elif file_info["type"] == "pdf":
                # Procesar PDF
                custom_prompt = prompt if prompt else "Extrae todo el texto visible en este documento."
                return self.process_pdf_with_mistral(file_info["file"], custom_prompt)
        
        return None

    @utils.enable_chat_history
    def main(self):
        # 1. Título y subtítulo (siempre visible en la parte superior)
        st.title("OCR con Mistral AI")
        st.write("Extrae texto de imágenes y documentos PDF utilizando la API de OCR de Mistral AI.")
        
        # Primero configurar el LLM en la barra lateral
        st.sidebar.markdown("### 🤖 Selecciona el modelo")
        self.llm = utils.configure_llm(key_suffix="_sidebar")
        
        # Obtener API key de Mistral
        self.mistral_api_key = utils.get_mistral_api_key(key_suffix="_sidebar")
        
        if not self.mistral_api_key:
            st.error("Se requiere una clave API de Mistral para usar esta funcionalidad.")
            st.info("Puedes obtener una clave API en https://console.mistral.ai/api-keys/")
            st.stop()
        
        # Luego mostrar instrucciones específicas para OCR
        with st.sidebar.expander("📷 Instrucciones de uso", expanded=True):
            st.markdown("""
            1. Sube una imagen o un documento PDF
            2. Espera a que se procese el archivo
            3. Revisa el texto extraído
            4. Opcionalmente, haz preguntas sobre el contenido
            
            **Limitaciones:**
            - Tamaño máximo de archivo: 5 MB
            - PDFs: se procesan hasta 5 páginas
            - Idiomas: soporta múltiples idiomas
            """)
        
        # Mostrar información del autor en la barra lateral (al final)
        try:
            from sidebar_info import show_author_info
            show_author_info()
        except ImportError:
            st.sidebar.warning("No se pudo cargar la información del autor.")
        
        # 2. Mostrar mensajes del historial (saludo inicial y conversación)
        for msg in st.session_state["ocr_messages"]:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
        
        # Mostrar selector de archivos
        file_info = self.display_file_uploader()
        
        # Opciones de procesamiento
        if file_info:
            with st.expander("Opciones de procesamiento", expanded=False):
                custom_prompt = st.text_area(
                    "Instrucción personalizada para el OCR",
                    value="Extrae todo el texto visible en esta imagen.",
                    help="Personaliza la instrucción para el modelo de OCR"
                )
                
                process_button = st.button("Procesar archivo", type="primary")
                
                if process_button:
                    # Procesar archivo
                    extracted_text = self.process_file(file_info, custom_prompt)
                    
                    if extracted_text:
                        # Añadir mensaje del usuario
                        user_message = f"He subido un archivo para extraer texto con la instrucción: '{custom_prompt}'"
                        st.session_state["ocr_messages"].append({"role": "user", "content": user_message})
                        
                        # Añadir respuesta del asistente
                        st.session_state["ocr_messages"].append({"role": "assistant", "content": extracted_text})
                        
                        # Recargar la página para mostrar los nuevos mensajes
                        st.rerun()
        
        # 3. Campo de entrada para nuevas preguntas (al final)
        user_query = st.chat_input(placeholder="Haz una pregunta sobre el texto extraído...")
        
        if user_query:
            # Añadir mensaje del usuario al historial
            st.session_state["ocr_messages"].append({"role": "user", "content": user_query})
            
            # Mostrar mensaje del usuario
            with st.chat_message("user"):
                st.write(user_query)
            
            # Generar respuesta
            with st.chat_message("assistant"):
                # Obtener el último texto extraído (si existe)
                extracted_text = None
                for msg in reversed(st.session_state["ocr_messages"]):
                    if msg["role"] == "assistant" and "Página" in msg["content"]:
                        extracted_text = msg["content"]
                        break
                
                if not extracted_text:
                    response = "No hay texto extraído para responder a tu pregunta. Por favor, sube primero un archivo."
                    st.write(response)
                else:
                    # Construir prompt para el LLM
                    prompt = f"""
                    Basado en el siguiente texto extraído de una imagen o PDF, responde a la pregunta del usuario.
                    
                    Texto extraído:
                    {extracted_text}
                    
                    Pregunta del usuario:
                    {user_query}
                    
                    Responde de manera concisa y clara. Si la información no está disponible en el texto, indícalo.
                    """
                    
                    # Crear un StreamHandler para mostrar la respuesta en tiempo real
                    st_cb = StreamHandler(st.empty())
                    
                    # Invocar el LLM
                    response = self.llm.invoke(prompt, streaming=True, callbacks=[st_cb])
                
                # Añadir respuesta al historial
                st.session_state["ocr_messages"].append({"role": "assistant", "content": response})


if __name__ == "__main__":
    obj = MistralOCRApp()
    obj.main()

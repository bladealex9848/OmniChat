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

# Inicializar mensajes - usando un enfoque más seguro
# Colocamos esto en una función para garantizar que se ejecute correctamente
def initialize_session_state():
    # Inicializar mensajes si no existen
    if "mistral_ocr_messages" not in st.session_state:
        st.session_state["mistral_ocr_messages"] = [
            {
                "role": "assistant",
                "content": "Hola, soy un asistente de OCR. Puedo extraer texto de imágenes y documentos PDF. Sube un archivo para comenzar.",
            }
        ]

    # Limpiar cualquier estado de sesión conflictivo
    if "ocr_messages" in st.session_state:
        # Migrar mensajes antiguos si existen
        if len(st.session_state["mistral_ocr_messages"]) <= 1:
            st.session_state["mistral_ocr_messages"] = st.session_state["ocr_messages"]
        # Eliminar la clave antigua
        del st.session_state["ocr_messages"]

# Llamar a la función de inicialización
initialize_session_state()

class MistralOCRApp:
    def __init__(self):
        # Evitamos usar sync_st_session() que puede causar problemas con el estado
        # utils.sync_st_session()
        self.llm = None
        self.mistral_api_key = None
        self.max_file_size = 5 * 1024 * 1024  # 5 MB en bytes

        # Limpiar cualquier estado de sesión que pueda estar causando conflictos
        keys_to_check = [
            "ocr_file_uploader",
            "mistral_ocr_file_uploader_8",
            "file_uploader"
        ]

        for key in keys_to_check:
            if key in st.session_state:
                try:
                    del st.session_state[key]
                except:
                    pass

    def save_file(self, file):
        """Guarda un archivo subido en una ubicación temporal"""
        folder = "tmp"
        if not os.path.exists(folder):
            os.makedirs(folder)

        file_path = f"./{folder}/{file.name}"
        with open(file_path, "wb") as f:
            f.write(file.getvalue())
        return file_path

    def get_image_base64(self, image):
        """Convierte una imagen PIL a base64"""
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return img_str

    def process_image_with_mistral(self, image, prompt="Extrae todo el texto visible en esta imagen."):
        """Procesa una imagen con la API de Mistral AI para OCR"""
        from mistralai import MistralClient
        from mistralai.models import ChatCompletionResponse

        # Convertir imagen a base64
        base64_image = self.get_image_base64(image)

        # Crear cliente de Mistral
        client = MistralClient(api_key=self.mistral_api_key)

        # Crear mensaje con la imagen usando la nueva estructura de la API
        messages = [
            {
                "role": "user",
                "content": [
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
                ]
            }
        ]

        # Llamar a la API de Mistral
        try:
            st.info("Enviando imagen a Mistral AI para OCR...")
            chat_response = client.chat(
                model="mistral-large-latest",
                messages=messages,
            )

            # Extraer el contenido de la respuesta
            if hasattr(chat_response, 'choices') and len(chat_response.choices) > 0:
                if hasattr(chat_response.choices[0], 'message') and hasattr(chat_response.choices[0].message, 'content'):
                    return chat_response.choices[0].message.content
                else:
                    # Alternativa si la estructura es diferente
                    return chat_response.choices[0].get('message', {}).get('content', '')
            else:
                st.warning("La respuesta de Mistral AI no tiene el formato esperado")
                st.write(f"Respuesta recibida: {chat_response}")
                return str(chat_response)
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
        """Muestra el selector de archivos en la barra lateral"""
        # Mostrar el selector de archivos en la barra lateral SIN USAR CLAVE
        # Esto evita completamente los problemas de StreamlitValueAssignmentNotAllowedError
        st.sidebar.markdown("### 📷 Cargar archivos para OCR")
        uploaded_file = st.sidebar.file_uploader(
            "Sube una imagen o PDF para extraer texto",
            type=["jpg", "jpeg", "png", "pdf"],
            # No usamos key para evitar conflictos
            help="Formatos soportados: JPG, JPEG, PNG, PDF. Tamaño máximo: 5 MB."
        )

        if uploaded_file is not None:
            # Verificar tamaño del archivo
            if uploaded_file.size > self.max_file_size:
                st.sidebar.error(f"El archivo es demasiado grande. El tamaño máximo permitido es 5 MB.")
                return None

            # Mostrar información del archivo en la barra lateral
            st.sidebar.success(f"✅ Archivo cargado correctamente")
            st.sidebar.info(f"📄 {uploaded_file.name} ({round(uploaded_file.size/1024, 1)} KB)")

            # Determinar el tipo de archivo
            file_type = uploaded_file.type
            st.sidebar.write(f"Tipo de archivo detectado: {file_type}")

            # Verificar si el tipo de archivo es None o vacío (puede ocurrir en algunos navegadores)
            if not file_type:
                # Intentar determinar el tipo por la extensión
                if uploaded_file.name.lower().endswith(('.jpg', '.jpeg', '.png')):
                    file_type = "image/jpeg"
                    st.sidebar.write("Tipo determinado por extensión: imagen")
                elif uploaded_file.name.lower().endswith('.pdf'):
                    file_type = "application/pdf"
                    st.sidebar.write("Tipo determinado por extensión: PDF")

            if file_type and (file_type.startswith("image") or
                             uploaded_file.name.lower().endswith(('.jpg', '.jpeg', '.png'))):
                # Es una imagen
                return {"type": "image", "file": uploaded_file}
            elif file_type and (file_type == "application/pdf" or
                                uploaded_file.name.lower().endswith('.pdf')):
                # Es un PDF
                return {"type": "pdf", "file": uploaded_file}
            else:
                # Tipo no reconocido
                st.sidebar.error(f"Tipo de archivo no reconocido: {file_type}")
                return None
        else:
            # Mostrar mensaje de ayuda cuando no hay archivos
            st.sidebar.info("👆 Sube una imagen o PDF para comenzar")

        return None

    def process_file(self, file_info, prompt=None):
        """Procesa el archivo según su tipo con manejo de errores mejorado"""
        if not file_info:
            st.error("No se ha proporcionado información del archivo")
            return None

        # Verificar que el archivo exista
        if "file" not in file_info or file_info["file"] is None:
            st.error("El archivo no está disponible")
            return None

        # Verificar que el tipo esté definido
        if "type" not in file_info or not file_info["type"]:
            st.error("No se ha podido determinar el tipo de archivo")
            return None

        # Mostrar información de depuración
        st.write(f"Procesando archivo: {file_info['file'].name} de tipo {file_info['type']}")

        # Guardar el archivo en disco para procesamiento más confiable
        try:
            file_path = self.save_file(file_info["file"])
            st.info(f"Archivo guardado temporalmente: {file_info['file'].name}")
        except Exception as e:
            st.error(f"Error al guardar el archivo: {str(e)}")
            return None

        # Procesar según el tipo de archivo
        with st.status(f"Procesando {file_info['file'].name}...", expanded=True) as status:
            try:
                status.update(label="Preparando archivo para OCR...", state="running")

                if file_info["type"] == "image":
                    # Procesar imagen
                    try:
                        # Abrir la imagen desde el archivo guardado
                        image = Image.open(file_path)
                        status.update(label="Enviando imagen a Mistral AI...", state="running")

                        # Usar prompt personalizado o predeterminado
                        custom_prompt = prompt if prompt else "Extrae todo el texto visible en esta imagen."
                        result = self.process_image_with_mistral(image, custom_prompt)

                        if result:
                            status.update(label="Imagen procesada correctamente", state="complete")
                            return result
                        else:
                            status.update(label="No se pudo extraer texto de la imagen", state="error")
                            return None
                    except Exception as e:
                        status.update(label=f"Error al procesar imagen: {str(e)}", state="error")
                        st.error(f"Error detallado: {str(e)}")
                        return None

                elif file_info["type"] == "pdf":
                    # Procesar PDF
                    try:
                        status.update(label="Leyendo PDF...", state="running")

                        # Abrir el PDF desde el archivo guardado
                        with open(file_path, "rb") as f:
                            pdf_bytes = f.read()

                        status.update(label="Enviando PDF a Mistral AI...", state="running")

                        # Usar prompt personalizado o predeterminado
                        custom_prompt = prompt if prompt else "Extrae todo el texto visible en este documento."

                        # Usar la API de Mistral para OCR
                        import base64
                        import requests
                        import json

                        # Codificar PDF en base64
                        encoded_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
                        pdf_url = f"data:application/pdf;base64,{encoded_pdf}"

                        # Preparar payload para la API
                        payload = {
                            "model": "mistral-ocr-latest",
                            "document": {"type": "document_url", "document_url": pdf_url},
                        }

                        # Configurar headers
                        headers = {
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {self.mistral_api_key}",
                        }

                        # Hacer la solicitud a la API
                        response = requests.post(
                            "https://api.mistral.ai/v1/ocr",
                            json=payload,
                            headers=headers,
                            timeout=90,  # Timeout ampliado para PDFs grandes
                        )

                        # Verificar respuesta
                        if response.status_code == 200:
                            result = response.json()

                            # Extraer texto del resultado
                            if "pages" in result and isinstance(result["pages"], list):
                                pages = result["pages"]
                                if pages and "markdown" in pages[0]:
                                    text = "\n\n".join(page.get("markdown", "") for page in pages if "markdown" in page)
                                    status.update(label="PDF procesado correctamente", state="complete")
                                    return text

                            # Si no se pudo extraer texto estructurado
                            status.update(label="No se pudo extraer texto estructurado del PDF", state="error")
                            return None
                        else:
                            error_message = f"Error en API OCR (código {response.status_code}): {response.text[:200]}"
                            status.update(label=error_message, state="error")
                            return None
                    except Exception as e:
                        status.update(label=f"Error al procesar PDF: {str(e)}", state="error")
                        st.error(f"Error detallado: {str(e)}")
                        return None
            except Exception as e:
                status.update(label=f"Error general: {str(e)}", state="error")
                st.error(f"Error inesperado: {str(e)}")
                return None

        return None

    def main(self):
        # Asegurarse de que el estado de sesión esté inicializado
        if "mistral_ocr_messages" not in st.session_state:
            initialize_session_state()

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

        # Mostrar selector de archivos en la barra lateral
        st.sidebar.markdown("---")
        file_info = self.display_file_uploader()

        # Depuración: Mostrar información sobre el archivo cargado
        if file_info:
            st.sidebar.markdown("---")
            st.sidebar.subheader("Información del archivo")
            st.sidebar.json({
                "nombre": file_info["file"].name,
                "tipo": file_info["type"],
                "tamaño": f"{round(file_info['file'].size/1024, 1)} KB"
            })

        # Mostrar información del autor en la barra lateral (al final)
        st.sidebar.markdown("---")
        try:
            from sidebar_info import show_author_info
            show_author_info()
        except ImportError:
            st.sidebar.warning("No se pudo cargar la información del autor.")

        # 2. Mostrar mensajes del historial (saludo inicial y conversación)
        # Implementación manual del historial de chat
        for i, msg in enumerate(st.session_state["mistral_ocr_messages"]):
            with st.chat_message(msg["role"]):
                # Si es el último mensaje del asistente y contiene texto extraído, mostrarlo en un expander
                if (msg["role"] == "assistant" and i > 0 and
                    ("PÁGINA" in msg["content"] or "Extrae todo el texto" in msg["content"])):
                    with st.expander("Texto extraído", expanded=False):
                        st.write(msg["content"])
                else:
                    st.write(msg["content"])

        # Opciones de procesamiento si hay un archivo cargado
        if file_info:
            # Crear dos columnas para mostrar la vista previa y las opciones
            col1, col2 = st.columns([2, 1])

            with col1:
                # Mostrar vista previa del archivo
                if file_info["type"] == "image":
                    st.image(file_info["file"], caption=f"Vista previa: {file_info['file'].name}", use_container_width=True)
                elif file_info["type"] == "pdf":
                    st.info(f"PDF cargado: {file_info['file'].name}")
                    st.caption("Los PDFs no tienen vista previa, pero serán procesados correctamente.")

            with col2:
                # Mostrar opciones de procesamiento
                st.subheader("Opciones de procesamiento")
                custom_prompt = st.text_area(
                    "Instrucción para el OCR",
                    value="Extrae todo el texto visible en esta imagen o documento.",
                    help="Personaliza la instrucción para el modelo de OCR"
                )

                process_button = st.button("Procesar archivo", type="primary", use_container_width=True)

            # Botón de procesamiento y resultados
            if process_button:
                # Procesar archivo
                extracted_text = self.process_file(file_info, custom_prompt)

                if extracted_text:
                    # Añadir mensaje del usuario
                    user_message = f"He subido {file_info['file'].name} para extraer texto con la instrucción: '{custom_prompt}'"
                    st.session_state["mistral_ocr_messages"].append({"role": "user", "content": user_message})

                    # Añadir respuesta del asistente
                    st.session_state["mistral_ocr_messages"].append({"role": "assistant", "content": extracted_text})

                    # Mostrar éxito
                    st.success("Texto extraído correctamente")

                    # Mostrar el texto extraído en un expander
                    with st.expander("Ver texto extraído", expanded=False):
                        st.markdown(extracted_text)

                    # Recargar la página para mostrar los nuevos mensajes
                    st.rerun()
                else:
                    st.error("No se pudo extraer texto del archivo. Intenta con otro archivo o verifica que el contenido sea legible.")
        else:
            # Mostrar mensaje de ayuda cuando no hay archivos
            st.info("👆 Por favor, carga una imagen o PDF en la barra lateral para comenzar.")

            # Mostrar ejemplos de uso
            with st.expander("Ver ejemplos de uso", expanded=False):
                st.markdown("""
                ### Ejemplos de uso:

                1. **Documentos escaneados**: Sube un PDF escaneado para extraer su contenido textual.
                2. **Imágenes de texto**: Sube fotos de documentos, páginas de libros o carteles.
                3. **Facturas y recibos**: Extrae información de facturas o recibos escaneados.
                4. **Tarjetas de presentación**: Digitaliza la información de tarjetas de presentación.

                Una vez extraído el texto, puedes hacer preguntas sobre su contenido usando el chat.
                """)

        # 3. Campo de entrada para nuevas preguntas (al final)
        user_query = st.chat_input(placeholder="Haz una pregunta sobre el texto extraído...")

        if user_query:
            # Añadir mensaje del usuario al historial
            st.session_state["mistral_ocr_messages"].append({"role": "user", "content": user_query})

            # Mostrar mensaje del usuario
            with st.chat_message("user"):
                st.write(user_query)

            # Generar respuesta
            with st.chat_message("assistant"):
                # Obtener el último texto extraído (si existe)
                extracted_text = None
                for msg in reversed(st.session_state["mistral_ocr_messages"]):
                    if msg["role"] == "assistant" and ("PÁGINA" in msg["content"] or "Extrae todo el texto" in msg["content"]):
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
                st.session_state["mistral_ocr_messages"].append({"role": "assistant", "content": response})


if __name__ == "__main__":
    try:
        # Asegurarse de que el estado de sesión esté inicializado correctamente
        if "mistral_ocr_messages" not in st.session_state:
            # Inicializar con un mensaje de bienvenida
            st.session_state["mistral_ocr_messages"] = [
                {
                    "role": "assistant",
                    "content": "Hola, soy un asistente de OCR. Puedo extraer texto de imágenes y documentos PDF. Sube un archivo para comenzar.",
                }
            ]

        # Limpiar cualquier estado de sesión que pueda estar causando conflictos
        # pero preservar mistral_ocr_messages
        mistral_messages = None
        if "mistral_ocr_messages" in st.session_state:
            mistral_messages = st.session_state["mistral_ocr_messages"]

        for key in list(st.session_state.keys()):
            if "file_uploader" in key or "ocr" in key:
                try:
                    del st.session_state[key]
                except:
                    pass

        # Restaurar mistral_ocr_messages
        if mistral_messages:
            st.session_state["mistral_ocr_messages"] = mistral_messages

        # Crear una nueva instancia de la aplicación
        obj = MistralOCRApp()
        obj.main()
    except Exception as e:
        st.error(f"Error al iniciar la aplicación: {str(e)}")
        st.info("Intenta recargar la página o limpiar la caché del navegador.")

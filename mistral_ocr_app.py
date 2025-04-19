import os
import streamlit as st
import base64
import json
import time
import tempfile
import requests
import traceback
import logging
import uuid
from pathlib import Path
import io
import mimetypes
from PIL import Image

# Configuración de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("MistralOCR")

# Versión de la aplicación
APP_VERSION = "1.0.0"

# Configuración inicial de la página
st.set_page_config(
    layout="wide",
    page_title="Mistral OCR App",
    page_icon="🔍",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://docs.mistral.ai/api/",
        "Report a bug": "https://github.com/bladealex9848/OmniChat/issues",
        "About": "Mistral OCR App v"
        + APP_VERSION
        + " - Desarrollada con Streamlit y Mistral AI API",
    },
)

# Inicializar variables de estado de sesión para persistencia
if "ocr_result" not in st.session_state:
    st.session_state["ocr_result"] = []
if "preview_src" not in st.session_state:
    st.session_state["preview_src"] = []
if "image_bytes" not in st.session_state:
    st.session_state["image_bytes"] = []
if "file_names" not in st.session_state:
    st.session_state["file_names"] = []
if "processing_complete" not in st.session_state:
    st.session_state["processing_complete"] = False
if "show_technical_details" not in st.session_state:
    st.session_state["show_technical_details"] = False

# Inyectar CSS personalizado
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0D47A1;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #E8F5E9;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .error-box {
        background-color: #FFEBEE;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .stButton>button {
        background-color: #1976D2;
        color: white;
        font-weight: 500;
    }
    .stButton>button:hover {
        background-color: #1565C0;
        color: white;
    }
    .download-button {
        display: inline-block;
        padding: 0.5rem 1rem;
        background-color: #1976D2;
        color: white;
        text-decoration: none;
        border-radius: 4px;
        font-weight: 500;
        text-align: center;
        margin: 0.25rem 0;
        width: 100%;
    }
    .download-button:hover {
        background-color: #1565C0;
        color: white;
    }
    .technical-info {
        font-family: monospace;
        background-color: #f5f5f5;
        padding: 10px;
        border-radius: 4px;
        margin: 10px 0;
        white-space: pre-wrap;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 16px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1976D2 !important;
        color: white !important;
    }
    /* Mejoras para visualización en dispositivos móviles */
    @media (max-width: 768px) {
        .stButton>button {
            width: 100%;
            margin: 5px 0;
        }
        .st-emotion-cache-16txtl3 {
            padding: 1rem 0.5rem;
        }
    }
</style>
""",
    unsafe_allow_html=True,
)

# ====================== FUNCIONES UTILITARIAS ======================


def get_mistral_api_key():
    """
    Obtiene la API key de Mistral de diferentes fuentes.
    Orden de prioridad: 1. Streamlit secrets, 2. Variables de entorno
    """
    try:
        # 1. Intentar obtener de Streamlit secrets
        if hasattr(st, "secrets") and "MISTRAL_API_KEY" in st.secrets:
            return st.secrets["MISTRAL_API_KEY"]
    except Exception as e:
        logger.warning(f"Error al obtener API key de secrets: {str(e)}")

    # 2. Intentar obtener de variables de entorno
    api_key = os.environ.get("MISTRAL_API_KEY")
    if api_key and api_key.strip():
        return api_key

    # 3. No se encontró API key
    return None


def validate_api_key(api_key):
    """
    Verifica la validez de la API key.
    """
    if not api_key:
        return False, "No se ha proporcionado API key"

    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        # Intentar una solicitud simple para verificar la clave con timeout para evitar bloqueos
        response = requests.get(
            "https://api.mistral.ai/v1/models", headers=headers, timeout=10
        )

        if response.status_code == 200:
            return True, "API key válida"
        elif response.status_code == 401:
            return False, "API key no válida o expirada"
        else:
            return False, f"Error verificando API key: código {response.status_code}"
    except requests.exceptions.ConnectionError:
        return (
            False,
            "Error de conexión al verificar la API key. Comprueba tu conexión a internet.",
        )
    except requests.exceptions.Timeout:
        return (
            False,
            "Timeout al verificar la API key. El servidor está tardando demasiado en responder.",
        )
    except Exception as e:
        logger.error(f"Error inesperado al validar API key: {str(e)}")
        return False, f"Error al validar API key: {str(e)}"


def prepare_image_for_ocr(file_data):
    """
    Prepara una imagen para ser procesada con OCR, asegurando formato óptimo.
    """
    try:
        # Abrir la imagen con PIL para procesamiento
        img = Image.open(io.BytesIO(file_data))

        # Determinar el mejor formato para salida
        save_format = "JPEG" if img.mode == "RGB" else "PNG"

        # Crear un buffer para guardar la imagen optimizada
        buffer = io.BytesIO()

        # Guardar la imagen en el buffer con el formato seleccionado
        if save_format == "JPEG":
            img.save(buffer, format="JPEG", quality=95)
        else:
            img.save(buffer, format="PNG")

        # Devolver los datos optimizados
        buffer.seek(0)
        return buffer.read(), f"image/{save_format.lower()}"

    except Exception as e:
        logger.warning(f"No se pudo optimizar la imagen: {str(e)}")
        return file_data, "image/jpeg"  # Formato por defecto


def create_download_link(data, filetype, filename):
    """
    Crea un enlace de descarga para los resultados.
    """
    try:
        b64 = base64.b64encode(data.encode()).decode()
        href = f'<a href="data:{filetype};base64,{b64}" download="{filename}" class="download-button">Descargar {filename}</a>'
        return href
    except Exception as e:
        logger.error(f"Error al crear enlace de descarga: {str(e)}")
        return f'<span style="color: red;">Error al crear enlace de descarga: {str(e)}</span>'


def extract_text_from_ocr_response(response):
    """
    Extrae texto de diferentes formatos de respuesta OCR.
    """
    try:
        # Caso 1: Si hay páginas con markdown
        if "pages" in response and isinstance(response["pages"], list):
            pages = response["pages"]
            if pages and "markdown" in pages[0]:
                markdown_text = "\n\n".join(
                    page.get("markdown", "") for page in pages if "markdown" in page
                )
                if markdown_text.strip():
                    return {"text": markdown_text, "format": "markdown"}

        # Caso 2: Si hay un texto plano en la respuesta
        if "text" in response:
            return {"text": response["text"], "format": "text"}

        # Caso 3: Si hay elementos (para formatos más estructurados)
        if "elements" in response:
            elements = response["elements"]
            if isinstance(elements, list):
                text_parts = []
                for element in elements:
                    if "text" in element:
                        text_parts.append(element["text"])
                return {"text": "\n".join(text_parts), "format": "elements"}

        # Caso 4: Si hay un campo 'content' principal
        if "content" in response:
            return {"text": response["content"], "format": "content"}

        # Caso 5: Si no se encuentra texto en el formato esperado, intentar examinar toda la respuesta
        response_str = json.dumps(response, indent=2)

        # Si la respuesta es muy grande, devolver un mensaje informativo
        if len(response_str) > 5000:
            return {
                "text": "La respuesta OCR contiene datos pero no en el formato esperado. Revisa los detalles técnicos para más información.",
                "format": "unknown",
                "raw_response": response,
            }

        # Intentar extraer cualquier texto encontrado en la respuesta
        extracted_text = extract_all_text_fields(response)
        if extracted_text:
            return {"text": extracted_text, "format": "extracted"}

        return {
            "text": "No se pudo encontrar texto en la respuesta OCR. Revisa los detalles técnicos.",
            "format": "unknown",
            "raw_response": response,
        }
    except Exception as e:
        logger.error(f"Error al extraer texto de la respuesta OCR: {str(e)}")
        return {"error": f"Error al procesar la respuesta: {str(e)}"}


def extract_all_text_fields(data, prefix="", max_depth=5, current_depth=0):
    """
    Función recursiva para extraer todos los campos de texto de un diccionario anidado.
    """
    # Evitar recursión infinita
    if current_depth > max_depth:
        return []

    result = []

    if isinstance(data, dict):
        for key, value in data.items():
            new_prefix = f"{prefix}.{key}" if prefix else key

            if isinstance(value, str) and len(value) > 1:
                result.append(f"{new_prefix}: {value}")
            elif (
                isinstance(value, (dict, list)) and value
            ):  # Solo recursión si hay contenido
                child_results = extract_all_text_fields(
                    value, new_prefix, max_depth, current_depth + 1
                )
                result.extend(child_results)

    elif isinstance(data, list):
        # Limitar número de elementos procesados en listas muy grandes
        max_items = 20
        for i, item in enumerate(data[:max_items]):
            new_prefix = f"{prefix}[{i}]"
            if isinstance(item, (dict, list)) and item:
                child_results = extract_all_text_fields(
                    item, new_prefix, max_depth, current_depth + 1
                )
                result.extend(child_results)
            elif isinstance(item, str) and len(item) > 1:
                result.append(f"{new_prefix}: {item}")

        # Indicar si se truncó la lista
        if len(data) > max_items:
            result.append(
                f"{prefix}: [... {len(data) - max_items} elementos adicionales omitidos]"
            )

    return "\n".join(result)


# ====================== FUNCIONES DE PROCESAMIENTO OCR ======================


def process_image_with_mistral_ocr(api_key, image_data, file_name):
    """
    Procesa una imagen utilizando la API OCR de Mistral.
    """
    with st.status("Procesando imagen con Mistral OCR...", expanded=True) as status:
        try:
            # Generar un ID único para el trabajo
            job_id = str(uuid.uuid4())
            logger.info(f"Procesando imagen {file_name} (ID: {job_id})")

            # Obtener un mime type adecuado para la imagen
            try:
                # Si image_data es un archivo subido, convertirlo a bytes
                if hasattr(image_data, "read"):
                    bytes_data = image_data.read()
                    image_data.seek(0)  # Reset file pointer
                else:
                    # Si ya es bytes, usarlo directamente
                    bytes_data = image_data

                # Intentar detectar el tipo MIME de la imagen
                image_format = Image.open(io.BytesIO(bytes_data)).format.lower()
                mime_type = f"image/{image_format}"
                status.update(label=f"Imagen detectada como {mime_type}")
            except Exception as e:
                logger.warning(f"Error al detectar formato de imagen: {str(e)}")
                # Si falla, usar un tipo genérico
                mime_type = "image/jpeg"
                bytes_data = (
                    image_data if not hasattr(image_data, "read") else image_data.read()
                )

            # Codificar la imagen a base64
            encoded_image = base64.b64encode(bytes_data).decode("utf-8")
            image_url = f"data:{mime_type};base64,{encoded_image}"

            # Preparar los datos para la solicitud
            payload = {
                "model": "mistral-ocr-latest",
                "document": {"type": "image_url", "image_url": image_url},
            }

            # Configurar los headers
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            }

            status.update(label="Enviando imagen a la API...")

            # Hacer la solicitud a la API de Mistral con timeout
            response = requests.post(
                "https://api.mistral.ai/v1/ocr",
                json=payload,
                headers=headers,
                timeout=60,  # 60 segundos de timeout para imágenes grandes
            )

            # Revisar si la respuesta fue exitosa
            if response.status_code == 200:
                result = response.json()
                status.update(label="Imagen procesada correctamente", state="complete")
                return extract_text_from_ocr_response(result)
            else:
                error_message = (
                    f"Error en API OCR (código {response.status_code}): {response.text}"
                )
                logger.error(error_message)
                status.update(label="Error al procesar la imagen", state="error")
                return {"error": error_message}

        except requests.exceptions.Timeout:
            error_message = (
                "Timeout al procesar la imagen. La operación tomó demasiado tiempo."
            )
            logger.error(error_message)
            status.update(label="Timeout al procesar la imagen", state="error")
            return {"error": error_message}

        except requests.exceptions.ConnectionError:
            error_message = "Error de conexión al procesar la imagen. Comprueba tu conexión a internet."
            logger.error(error_message)
            status.update(label="Error de conexión", state="error")
            return {"error": error_message}

        except Exception as e:
            error_message = f"Error al procesar imagen: {str(e)}"
            logger.error(f"{error_message}\n{traceback.format_exc()}")
            status.update(label=f"Error: {str(e)}", state="error")
            return {"error": error_message}


def process_pdf_with_mistral_ocr(api_key, pdf_data, file_name):
    """
    Procesa un PDF utilizando la API OCR de Mistral.
    """
    with st.status("Procesando PDF con Mistral OCR...", expanded=True) as status:
        try:
            # Generar un ID único para el trabajo
            job_id = str(uuid.uuid4())
            logger.info(f"Procesando PDF {file_name} (ID: {job_id})")

            # Si pdf_data es un archivo subido, convertirlo a bytes
            if hasattr(pdf_data, "read"):
                bytes_data = pdf_data.read()
                pdf_data.seek(0)  # Reset file pointer
            else:
                # Si ya es bytes, usarlo directamente
                bytes_data = pdf_data

            # Codificar el PDF a base64
            encoded_pdf = base64.b64encode(bytes_data).decode("utf-8")
            pdf_url = f"data:application/pdf;base64,{encoded_pdf}"

            # Preparar los datos para la solicitud
            payload = {
                "model": "mistral-ocr-latest",
                "document": {"type": "document_url", "document_url": pdf_url},
            }

            # Configurar los headers
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            }

            status.update(label="Enviando PDF a la API...")

            # Hacer la solicitud a la API de Mistral con timeout
            response = requests.post(
                "https://api.mistral.ai/v1/ocr",
                json=payload,
                headers=headers,
                timeout=120,  # 120 segundos de timeout para PDFs grandes
            )

            # Revisar si la respuesta fue exitosa
            if response.status_code == 200:
                result = response.json()
                status.update(label="PDF procesado correctamente", state="complete")
                return extract_text_from_ocr_response(result)
            else:
                error_message = (
                    f"Error en API OCR (código {response.status_code}): {response.text}"
                )
                logger.error(error_message)
                status.update(label="Error al procesar el PDF", state="error")
                return {"error": error_message}

        except requests.exceptions.Timeout:
            error_message = (
                "Timeout al procesar el PDF. La operación tomó demasiado tiempo."
            )
            logger.error(error_message)
            status.update(label="Timeout al procesar el PDF", state="error")
            return {"error": error_message}

        except requests.exceptions.ConnectionError:
            error_message = "Error de conexión al procesar el PDF. Comprueba tu conexión a internet."
            logger.error(error_message)
            status.update(label="Error de conexión", state="error")
            return {"error": error_message}

        except Exception as e:
            error_message = f"Error al procesar PDF: {str(e)}"
            logger.error(f"{error_message}\n{traceback.format_exc()}")
            status.update(label=f"Error: {str(e)}", state="error")
            return {"error": error_message}


def process_document(api_key, source, source_type, optimize_images=True):
    """
    Función principal para procesar un documento (imagen o PDF).
    """
    file_bytes = None
    file_type = None
    file_name = None

    try:
        # Determinar el tipo de archivo y nombre
        if source_type == "Archivo local":
            file_name = source.name
            mime = mimetypes.guess_type(file_name)[0]
            if mime == "application/pdf":
                file_type = "PDF"
            elif mime and mime.startswith("image/"):
                file_type = "Imagen"
            else:
                logger.warning(f"Tipo de archivo no soportado: {mime} para {file_name}")
                return {
                    "success": False,
                    "result_text": f"Tipo de archivo no soportado: {file_name}",
                    "preview_src": "",
                    "file_name": file_name,
                    "file_bytes": None,
                    "raw_response": None,
                }
        elif source_type == "URL":
            file_name = source.split("/")[-1]
            if source.lower().endswith(".pdf"):
                file_type = "PDF"
            else:
                file_type = "Imagen"  # Asumir imagen para otras URLs por simplicidad
        else:
            return {
                "success": False,
                "result_text": "Tipo de fuente desconocido.",
                "preview_src": "",
                "file_name": "Error",
                "file_bytes": None,
                "raw_response": None,
            }

        # Preparar el documento según el tipo y la fuente
        if file_type == "PDF":
            if source_type == "URL":
                # TODO: Implementar descarga de PDF desde URL
                return {
                    "success": False,
                    "result_text": "Procesamiento de PDF desde URL no implementado aún.",
                    "preview_src": "",
                    "file_name": file_name,
                    "file_bytes": None,
                    "raw_response": None,
                }
            else:
                try:
                    # Procesar el PDF con la API de Mistral
                    ocr_response = process_pdf_with_mistral_ocr(
                        api_key, source, file_name
                    )
                    preview_src = f"data:application/pdf;base64,{base64.b64encode(source.read()).decode('utf-8')}"
                    source.seek(0)  # Reiniciar el cursor del archivo
                except Exception as e:
                    logger.error(f"Error al procesar PDF: {str(e)}")
                    return {
                        "success": False,
                        "result_text": f"Error al procesar el PDF: {str(e)}",
                        "preview_src": "",
                        "file_name": file_name,
                        "file_bytes": None,
                        "raw_response": None,
                    }
        elif file_type == "Imagen":
            if source_type == "URL":
                # TODO: Implementar descarga de imagen desde URL
                return {
                    "success": False,
                    "result_text": "Procesamiento de imagen desde URL no implementado aún.",
                    "preview_src": "",
                    "file_name": file_name,
                    "file_bytes": None,
                    "raw_response": None,
                }
            else:
                try:
                    # Leer los bytes de la imagen
                    file_bytes = source.read()
                    source.seek(0)  # Reiniciar el cursor del archivo

                    # Optimizar la imagen si está habilitado
                    if optimize_images:
                        file_bytes, mime_type = prepare_image_for_ocr(file_bytes)
                    else:
                        mime_type = source.type

                    # Procesar la imagen con la API de Mistral
                    ocr_response = process_image_with_mistral_ocr(
                        api_key, file_bytes, file_name
                    )

                    # Preparar la vista previa
                    encoded_image = base64.b64encode(file_bytes).decode("utf-8")
                    preview_src = f"data:{mime_type};base64,{encoded_image}"
                except Exception as e:
                    logger.error(f"Error al procesar imagen: {str(e)}")
                    return {
                        "success": False,
                        "result_text": f"Error al procesar la imagen: {str(e)}",
                        "preview_src": "",
                        "file_name": file_name,
                        "file_bytes": None,
                        "raw_response": None,
                    }
        else:
            return {
                "success": False,
                "result_text": f"Tipo de archivo no soportado para {file_name}.",
                "preview_src": "",
                "file_name": file_name,
                "file_bytes": None,
                "raw_response": None,
            }

        # Procesar la respuesta OCR
        if "error" in ocr_response:
            result_text = f"Error al procesar {file_name}: {ocr_response['error']}"
            success = False
            raw_response = None
        else:
            if "text" in ocr_response:
                result_text = ocr_response["text"]
                success = True
                raw_response = ocr_response.get("raw_response")
            else:
                result_text = f"No se encontró texto en {file_name}."
                success = False
                raw_response = ocr_response.get("raw_response")

        logger.info(
            f"Documento {file_name} procesado: {'Exitoso' if success else 'Fallido'}"
        )
        return {
            "success": success,
            "result_text": result_text,
            "preview_src": preview_src if "preview_src" in locals() else "",
            "file_name": file_name,
            "file_bytes": file_bytes,
            "raw_response": raw_response,
        }

    except Exception as e:
        error_msg = str(e)
        logger.error(
            f"Error inesperado procesando documento: {error_msg}\n{traceback.format_exc()}"
        )
        return {
            "success": False,
            "result_text": f"Error inesperado: {error_msg}",
            "preview_src": "",
            "file_name": file_name if file_name else "documento",
            "file_bytes": file_bytes,
            "raw_response": None,
        }


# ====================== INTERFAZ DE USUARIO ======================

# Título principal en el área de contenido
st.markdown("<h1 class='main-header'>🔍 Mistral OCR App</h1>", unsafe_allow_html=True)
st.markdown(
    "<p>Extracción de texto de imágenes y documentos PDF utilizando la API de Mistral AI</p>",
    unsafe_allow_html=True,
)

# Obtener la API key
api_key = get_mistral_api_key()

# ====================== BARRA LATERAL (CONFIGURACIÓN) ======================
with st.sidebar:
    try:
        st.image("assets/logo.svg", width=150)
    except Exception as e:
        st.write("Mistral OCR")
        if st.session_state.get("show_technical_details", False):
            st.error(f"Error al cargar logo: {str(e)}")
    st.header("Configuración")

    # UI para la API key - solo se muestra si no está en secrets o variables de entorno
    if not api_key:
        api_key_input = st.text_input(
            "API key de Mistral",
            value="",
            type="password",
            help="Tu API key de Mistral. Se utilizará para procesar los documentos.",
        )

        if not api_key_input:
            st.info("Por favor, introduce tu API key de Mistral para continuar.")

            # Instrucciones para obtener API key
            with st.expander("🔑 ¿Cómo obtener una API key?"):
                st.markdown(
                    """
                1. Visita [mistral.ai](https://mistral.ai) y crea una cuenta
                2. Navega a la sección de API Keys
                3. Genera una nueva API key
                4. Copia y pégala aquí

                También puedes configurar tu API key como:
                - Variable de entorno: `MISTRAL_API_KEY`
                - Secreto de Streamlit: `.streamlit/secrets.toml`
                """
                )
        else:
            # Verificar la API key ingresada
            valid, message = validate_api_key(api_key_input)
            if valid:
                st.success(f"✅ {message}")
                api_key = api_key_input
            else:
                st.warning(f"⚠️ {message}")
    else:
        # Verificar silenciosamente la API key existente
        valid, message = validate_api_key(api_key)
        if valid:
            st.success("✅ API key configurada correctamente")
        else:
            st.error(f"❌ La API key configurada no es válida: {message}")

    # Método de carga
    st.subheader("Método de carga")
    source_type = st.radio(
        "Selecciona el método de carga",
        options=["Archivo local", "URL"],
        help="Selecciona URL para procesar archivos desde internet o Archivo local para subir desde tu dispositivo.",
    )

    # Opciones avanzadas
    st.header("⚙️ Opciones avanzadas")

    # Opciones generales
    show_technical_details = st.checkbox(
        "Mostrar detalles técnicos",
        value=st.session_state.get("show_technical_details", False),
        help="Muestra información técnica detallada durante el procesamiento",
    )
    # Actualizar el estado de sesión
    st.session_state["show_technical_details"] = show_technical_details

    optimize_images = st.checkbox(
        "Optimizar imágenes",
        value=True,
        help="Optimiza las imágenes antes de enviarlas para OCR (recomendado)",
    )

    # Información de la aplicación
    with st.expander("ℹ️ Acerca de Mistral OCR"):
        st.markdown(
            """
        ### Características:
        - Extracción de texto con preservación de estructura
        - Soporte para PDF e imágenes
        - Optimización de imágenes

        ### Limitaciones:
        - PDFs hasta 50 MB
        - Máximo 1,000 páginas por documento
        """
        )

    # Versión de la app
    st.caption(f"Mistral OCR App v{APP_VERSION}")

# ====================== ÁREA PRINCIPAL ======================

# Verificar si tenemos API key válida para continuar
if not api_key:
    st.warning("⚠️ Se requiere una API key válida para utilizar la aplicación.")

    # Mostrar información sobre la aplicación mientras no hay API key
    st.info(
        "Esta aplicación permite extraer texto de documentos PDF e imágenes usando tecnología OCR avanzada."
    )

    with st.expander("🔍 ¿Qué puedes hacer con Mistral OCR?"):
        st.markdown(
            """
        - **Digitalizar documentos** escaneados o fotografiados
        - **Extraer texto** de facturas, recibos, contratos, etc.
        - **Preservar el formato** del documento original
        - **Procesar documentos** en lote
        - **Descargar resultados** en diferentes formatos
        """
        )

    # Detener la ejecución hasta que tengamos una API key
    st.stop()

# Interfaz para cargar documentos
st.header("1️⃣ Cargar documentos")

input_url = ""
uploaded_files = []

if source_type == "URL":
    input_url = st.text_area(
        "Introduce URLs (una por línea)",
        help="Introduce las URLs de los documentos a procesar",
    )
    st.info(
        "⚠️ El procesamiento desde URL está en desarrollo. Por favor, usa la carga de archivos locales."
    )

    # Desactivar temporalmente el procesamiento desde URL
    st.warning("El procesamiento desde URL no está disponible en esta versión.")
    has_input = False
else:
    acceptable_types = ["pdf", "jpg", "jpeg", "png"]
    uploaded_files = st.file_uploader(
        "Sube archivos",
        type=acceptable_types,
        accept_multiple_files=True,
        help=f"Formatos aceptados: {', '.join(acceptable_types)} (el tipo de archivo se detectará automáticamente)",
    )
    has_input = bool(uploaded_files)

# Botón de procesamiento
st.header("2️⃣ Procesar")

process_button = st.button(
    "📄 Procesar documentos",
    help="Inicia el procesamiento OCR",
    use_container_width=True,
    disabled=not api_key or not has_input,
)

# ====================== LÓGICA DE PROCESAMIENTO ======================

if process_button:
    # Preparar fuentes
    try:
        sources = uploaded_files  # Por ahora solo archivos locales

        if not sources:
            st.error("No se encontraron fuentes válidas para procesar.")
            st.stop()

        # Reiniciar estados
        st.session_state["ocr_result"] = []
        st.session_state["preview_src"] = []
        st.session_state["image_bytes"] = []
        st.session_state["file_names"] = []
        st.session_state["processing_complete"] = False

        total_files = len(sources)
        st.info(f"Procesando {total_files} documento(s)...")

        # Configurar barra de progreso
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Procesar documentos de forma secuencial con mejor información de progreso
        results = []

        for idx, source in enumerate(sources):
            # Actualizar progreso
            progress_value = idx / total_files
            progress_bar.progress(
                progress_value, text=f"Procesando {idx+1}/{total_files}"
            )

            # Nombre de fuente para mostrar
            source_name = source.name
            status_text.text(f"Procesando archivo: {source_name}")

            # Procesar documento
            result = process_document(
                api_key,
                source,
                source_type,
                optimize_images,
            )

            results.append(result)

            # Actualizar listas de resultados
            st.session_state["ocr_result"].append(result["result_text"])
            st.session_state["preview_src"].append(result["preview_src"])
            st.session_state["file_names"].append(result["file_name"])
            if result["file_bytes"] is not None:
                st.session_state["image_bytes"].append(result["file_bytes"])

        # Marcar procesamiento como completado
        st.session_state["processing_complete"] = True

        # Actualizar progreso final
        progress_bar.progress(1.0, text="¡Procesamiento completado!")

        # Mostrar resumen
        success_count = sum(1 for r in results if r["success"])
        if success_count == total_files:
            st.success(
                f"✅ ¡Procesamiento completado con éxito! Se procesaron {total_files} documento(s)."
            )
        else:
            st.warning(
                f"⚠️ Procesamiento completado con {total_files - success_count} error(es). Se procesaron {success_count} de {total_files} documento(s) correctamente."
            )

    except Exception as e:
        st.error(f"Error al preparar documentos para procesamiento: {str(e)}")
        if st.session_state["show_technical_details"]:
            with st.expander("Detalles técnicos del error"):
                st.code(traceback.format_exc())

# ====================== VISUALIZACIÓN DE RESULTADOS ======================

# Mostrar resultados si están disponibles
if st.session_state.get("processing_complete") and st.session_state.get("ocr_result"):
    st.header("3️⃣ Resultados")

    try:
        if len(st.session_state["file_names"]) > 0:
            # Usar tabs para múltiples documentos
            if len(st.session_state["file_names"]) > 1:
                tabs = st.tabs(
                    [
                        f"Doc {idx+1}: {name}"
                        for idx, name in enumerate(st.session_state["file_names"])
                    ]
                )
            else:
                # Para un solo documento, crear un contenedor sin tabs
                tabs = [st.container()]

            for idx, tab in enumerate(tabs):
                with tab:
                    # Dividir el espacio para previsualización y texto
                    col1, col2 = st.columns([1, 1])

                    with col1:
                        st.subheader("Vista previa del documento")

                        if (
                            idx < len(st.session_state["preview_src"])
                            and st.session_state["preview_src"][idx]
                        ):
                            file_name = st.session_state["file_names"][idx]

                            if "pdf" in file_name.lower():
                                # Solución para PDFs en Streamlit Cloud
                                pdf_display_html = f"""
                                <div style="border: 1px solid #ddd; border-radius: 5px; padding: 20px; text-align: center;">
                                    <p style="margin-bottom: 15px;">Vista previa directa no disponible</p>
                                    <a href="{st.session_state["preview_src"][idx]}"
                                       target="_blank"
                                       style="display: inline-block; padding: 10px 20px;
                                              background-color: #1976D2; color: white;
                                              text-decoration: none; border-radius: 4px;
                                              font-weight: 500;">
                                        Abrir PDF en nueva pestaña
                                    </a>
                                </div>
                                """
                                st.markdown(pdf_display_html, unsafe_allow_html=True)
                            else:
                                # Para imágenes
                                try:
                                    if idx < len(
                                        st.session_state.get("image_bytes", [])
                                    ):
                                        st.image(
                                            st.session_state["image_bytes"][idx],
                                            caption=f"Imagen original: {file_name}",
                                            use_container_width=True,
                                        )
                                    elif st.session_state["preview_src"][idx]:
                                        st.image(
                                            st.session_state["preview_src"][idx],
                                            caption=f"Imagen original: {file_name}",
                                            use_container_width=True,
                                        )
                                    else:
                                        st.info(
                                            "Vista previa no disponible para este documento."
                                        )
                                except Exception as e:
                                    st.error(f"Error al mostrar imagen: {str(e)}")
                                    st.info(
                                        "Vista previa no disponible debido a un error."
                                    )
                        else:
                            st.info("Vista previa no disponible para este documento.")

                    with col2:
                        st.subheader(f"Texto extraído")

                        if idx < len(st.session_state["ocr_result"]):
                            result_text = st.session_state["ocr_result"][idx]

                            if not result_text.startswith("Error:"):
                                # Añadir contador de caracteres
                                char_count = len(result_text)
                                word_count = len(result_text.split())
                                st.caption(
                                    f"{word_count} palabras | {char_count} caracteres"
                                )

                            # Texto área con resultado
                            st.text_area(
                                label="",
                                value=result_text,
                                height=400,
                                key=f"text_area_{idx}",
                            )

                            # Opciones de descarga para resultados exitosos
                            if not result_text.startswith("Error"):
                                st.subheader("Descargar resultados")

                                try:
                                    # Nombre base para archivos de descarga
                                    base_filename = st.session_state["file_names"][
                                        idx
                                    ].split(".")[0]

                                    # Opciones de descarga con mejor UI
                                    download_col1, download_col2, download_col3 = (
                                        st.columns(3)
                                    )

                                    with download_col1:
                                        json_data = json.dumps(
                                            {"ocr_result": result_text},
                                            ensure_ascii=False,
                                            indent=2,
                                        )
                                        st.markdown(
                                            create_download_link(
                                                json_data,
                                                "application/json",
                                                f"{base_filename}.json",
                                            ),
                                            unsafe_allow_html=True,
                                        )

                                    with download_col2:
                                        st.markdown(
                                            create_download_link(
                                                result_text,
                                                "text/plain",
                                                f"{base_filename}.txt",
                                            ),
                                            unsafe_allow_html=True,
                                        )

                                    with download_col3:
                                        st.markdown(
                                            create_download_link(
                                                result_text,
                                                "text/markdown",
                                                f"{base_filename}.md",
                                            ),
                                            unsafe_allow_html=True,
                                        )
                                except Exception as e:
                                    st.error(
                                        f"Error al crear enlaces de descarga: {str(e)}"
                                    )
                        else:
                            st.error(
                                "No hay resultados disponibles para este documento."
                            )

    except Exception as e:
        st.error(f"Error al mostrar resultados: {str(e)}")
        if st.session_state["show_technical_details"]:
            with st.expander("Detalles técnicos del error"):
                st.code(traceback.format_exc())

# ====================== PANTALLA INICIAL ======================
# Si no hay procesamiento completado, mostrar información de bienvenida
if not st.session_state.get("processing_complete"):
    # Crear columnas para organizar el contenido
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(
            """
        ## Bienvenido a Mistral OCR

        Esta aplicación te permite extraer texto de documentos PDF e imágenes utilizando
        la tecnología OCR avanzada de Mistral AI.

        ### Características principales:
        - Extracción de texto con preservación de formato
        - Soporte para documentos escaneados
        - Procesamiento de imágenes optimizado
        - Múltiples formatos de descarga
        """
        )

    with col2:
        # Imagen ilustrativa
        try:
            st.image(
                "https://images.unsplash.com/photo-1568667256549-094345857637?w=500",
                caption="OCR y extracción de texto",
                use_container_width=True,
            )
        except Exception:
            # Si no se puede cargar la imagen, mostrar un mensaje alternativo
            st.info("Mistral OCR - Digitaliza tus documentos")

# Información adicional
st.markdown("---")
with st.expander("🔧 Solución de problemas"):
    st.markdown(
        """
    Si encuentras problemas al usar esta aplicación, intenta lo siguiente:

    1. **Error al procesar imágenes**:
       - Asegúrate de que la imagen tenga buen contraste y resolución
       - Activa la opción "Optimizar imágenes" en las opciones avanzadas

    2. **Error 404 (Not Found)**:
       - Verifica que tengas acceso a la API de OCR en tu plan de Mistral

    3. **Error de API key**:
       - Verifica que tu API key de Mistral sea válida y esté correctamente introducida
       - Asegúrate de que la API key tenga permisos suficientes

    4. **Error de formato**:
       - Asegúrate de que tus archivos sean compatibles (PDF, JPG, PNG)
       - Verifica que los archivos no estén corruptos

    5. **Error de tamaño**:
       - Los archivos no deben exceder 50 MB
       - Intenta dividir documentos grandes

    Para más información, consulta la [documentación oficial de Mistral AI](https://docs.mistral.ai).
    """
    )

# Versión y créditos
st.markdown("---")
st.markdown(
    f"""
<div style="text-align: center; color: #666;">
    <p>Mistral OCR App v{APP_VERSION} | Desarrollada con Streamlit, Mistral AI API y procesamiento avanzado de imágenes</p>
</div>
""",
    unsafe_allow_html=True,
)

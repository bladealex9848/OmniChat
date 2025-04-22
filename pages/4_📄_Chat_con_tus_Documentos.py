import os
import sys

# Añadir el directorio raíz al path para poder importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils
import streamlit as st
from streaming import StreamHandler

# Importaciones de LangChain
try:
    # Intentar importar desde las nuevas ubicaciones
    from langchain.memory import ConversationBufferMemory
    from langchain_core.runnables import RunnablePassthrough
    from langchain.chains import ConversationalRetrievalChain
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_community.vectorstores import FAISS
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    # Fallback a las ubicaciones antiguas
    from langchain.memory import ConversationBufferMemory
    from langchain.chains import ConversationalRetrievalChain
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_community.vectorstores import FAISS
    from langchain_text_splitters import RecursiveCharacterTextSplitter

# Importar HuggingFaceEmbeddings desde langchain_huggingface si está disponible
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    # Fallback a la versión antigua si la nueva no está disponible
    from langchain_community.embeddings import HuggingFaceEmbeddings

    st.warning(
        "Se está utilizando una versión obsoleta de HuggingFaceEmbeddings. "
        "Considera actualizar a langchain-huggingface para mejor compatibilidad."
    )

# Configuración de la página (debe ser la primera llamada a Streamlit)
st.set_page_config(page_title="ChatPDF", page_icon="📄")

# Inicializar mensajes si no existen
if "doc_chat_messages" not in st.session_state:
    st.session_state["doc_chat_messages"] = [
        {
            "role": "assistant",
            "content": "Hola, soy un asistente virtual. ¿En qué puedo ayudarte hoy?",
        }
    ]

class CustomDataChatbot:

    def __init__(self):
        utils.sync_st_session()
        # No configuramos el LLM aquí para evitar duplicación
        self.llm = None

    def save_file(self, file):
        folder = "tmp"
        if not os.path.exists(folder):
            os.makedirs(folder)

        file_path = f"./{folder}/{file.name}"
        with open(file_path, "wb") as f:
            f.write(file.getvalue())
        return file_path

    @st.spinner("Analizando documentos...")
    def setup_qa_chain(self, uploaded_files):
        # Cargar documentos
        docs = []
        for file in uploaded_files:
            try:
                file_path = self.save_file(file)
                loader = PyPDFLoader(file_path)
                docs.extend(loader.load())
            except Exception as e:
                st.error(f"Error al cargar el archivo {file.name}: {str(e)}")
                st.info(
                    "Intenta con otro archivo PDF o verifica que el archivo no esté dañado."
                )

        # Verificar si se cargaron documentos
        if not docs:
            st.error(
                "No se pudieron cargar documentos. Por favor, verifica que los archivos sean PDFs válidos."
            )
            st.stop()

        # Dividir documentos
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )
        splits = text_splitter.split_documents(docs)

        # Verificar si hay fragmentos después de dividir
        if not splits:
            st.warning(
                "No se pudieron extraer fragmentos de texto de los documentos. Intentando con OCR..."
            )

            # Crear una función para procesar con OCR sin importar el módulo completo
            try:
                # Importar solo las funciones necesarias sin importar el módulo completo
                import base64
                import requests
                from langchain_core.documents import Document

                # Función para obtener la API key de Mistral
                def get_mistral_api_key_local():
                    # Intentar obtener de Streamlit secrets
                    if hasattr(st, "secrets") and "MISTRAL_API_KEY" in st.secrets:
                        return st.secrets["MISTRAL_API_KEY"]
                    # Intentar obtener de variables de entorno
                    api_key = os.environ.get("MISTRAL_API_KEY")
                    if api_key and api_key.strip():
                        return api_key
                    return None

                # Función para procesar PDF con OCR
                def process_pdf_with_ocr(api_key, pdf_data, file_name):
                    # Usar un contenedor normal en lugar de un status para evitar anidamiento de expanders
                    st.write(f"Procesando {file_name} con OCR de Mistral...")
                    progress_bar = st.progress(0, text="Iniciando procesamiento OCR...")

                    try:
                        # Si pdf_data es un archivo subido, convertirlo a bytes
                        if hasattr(pdf_data, "read"):
                            bytes_data = pdf_data.read()
                            pdf_data.seek(0)  # Reset file pointer
                        else:
                            # Si ya es bytes, usarlo directamente
                            bytes_data = pdf_data

                        progress_bar.progress(25, text="Preparando documento...")

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

                        progress_bar.progress(50, text="Enviando PDF a la API...")

                        # Hacer la solicitud a la API de Mistral con timeout
                        response = requests.post(
                            "https://api.mistral.ai/v1/ocr",
                            json=payload,
                            headers=headers,
                            timeout=120,  # 120 segundos de timeout para PDFs grandes
                        )

                        progress_bar.progress(75, text="Procesando respuesta...")

                        # Revisar si la respuesta fue exitosa
                        if response.status_code == 200:
                            result = response.json()
                            progress_bar.progress(100, text="PDF procesado correctamente")

                            # Extraer texto del resultado
                            if "pages" in result and isinstance(result["pages"], list):
                                pages = result["pages"]
                                if pages and "markdown" in pages[0]:
                                    text = "\n\n".join(page.get("markdown", "") for page in pages if "markdown" in page)
                                    return {"text": text}
                            elif "text" in result:
                                return {"text": result["text"]}
                            else:
                                return {"error": "No se pudo extraer texto del resultado OCR"}
                        else:
                            error_message = f"Error en API OCR (código {response.status_code}): {response.text}"
                            progress_bar.progress(100, text="Error al procesar el PDF")
                            return {"error": error_message}
                    except Exception as e:
                        error_message = f"Error al procesar PDF: {str(e)}"
                        progress_bar.progress(100, text=f"Error: {str(e)}")
                        return {"error": error_message}

                # Obtener la API key de Mistral
                api_key = get_mistral_api_key_local()

                if not api_key:
                    st.error("Se requiere una API key de Mistral para usar OCR. Configúrala en secrets.toml.")
                    st.stop()

                # Procesar cada documento con OCR
                ocr_docs = []
                for file in uploaded_files:
                    try:
                        file_path = self.save_file(file)
                        with open(file_path, "rb") as f:
                            file_bytes = f.read()

                        # Usar OCR para extraer texto
                        ocr_result = process_pdf_with_ocr(api_key, file_bytes, file.name)

                        if "error" in ocr_result:
                            st.error(f"Error en OCR: {ocr_result['error']}")
                            continue

                        # Extraer texto del resultado OCR
                        if "text" in ocr_result and ocr_result["text"]:
                            # Crear un documento con el texto extraído
                            doc = Document(
                                page_content=ocr_result["text"],
                                metadata={"source": file_path, "page": 1}
                            )
                            ocr_docs.append(doc)
                            st.success(f"Texto extraído con éxito de {file.name} usando OCR")
                    except Exception as e:
                        st.error(f"Error al procesar {file.name} con OCR: {str(e)}")

                # Si se obtuvieron documentos con OCR, usarlos
                if ocr_docs:
                    # Dividir los documentos OCR
                    splits = text_splitter.split_documents(ocr_docs)
                    st.success(f"Se obtuvieron {len(splits)} fragmentos de texto usando OCR")
                else:
                    st.error("No se pudo extraer texto con OCR. Por favor, intenta con otros documentos.")
                    st.stop()
            except Exception as e:
                st.error(f"Error al intentar usar OCR: {str(e)}")
                st.stop()

        # Crear embeddings y almacenar en vectordb
        try:
            # Intentar con el modelo principal
            st.info("Usando modelo de embeddings multilingüe...")
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            )
            vectordb = FAISS.from_documents(splits, embeddings)
        except IndexError:
            # Intentar con un modelo alternativo más simple
            try:
                st.warning(
                    "El modelo principal falló. Intentando con un modelo alternativo..."
                )
                embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
                vectordb = FAISS.from_documents(splits, embeddings)
            except Exception as e2:
                st.error(f"Error con el modelo alternativo: {str(e2)}")
                st.error(
                    "Error al procesar los embeddings. Es posible que los documentos estén vacíos o no contengan texto procesable."
                )
                st.stop()
        except Exception as e:
            st.error(f"Error al crear la base de datos vectorial: {str(e)}")
            # Intentar con un enfoque más simple
            try:
                st.warning("Intentando con un enfoque alternativo...")
                # Usar un modelo más simple y robusto
                embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
                # Intentar con chunks más pequeños
                smaller_splits = text_splitter.split_documents(docs, chunk_size=500)
                vectordb = FAISS.from_documents(smaller_splits, embeddings)
            except Exception as e2:
                st.error(f"Error con el enfoque alternativo: {str(e2)}")
                st.stop()

        # Definir recuperador
        retriever = vectordb.as_retriever(
            search_type="mmr", search_kwargs={"k": 2, "fetch_k": 4}
        )

        # Configurar memoria para conversación contextual
        memory = ConversationBufferMemory(
            memory_key="chat_history", output_key="answer", return_messages=True
        )

        # Configurar LLM y cadena de QA
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=memory,
            return_source_documents=True,
            verbose=True,
        )
        return qa_chain

    def main(self):
        # 1. Título y subtítulo (siempre visible en la parte superior)
        st.title("Chatea con tus documentos (RAG Básico)")
        st.write(
            "Tiene acceso a documentos personalizados y puede responder a las consultas de los usuarios refiriéndose al contenido de esos documentos"
        )

        # Primero configurar el LLM en la barra lateral
        st.sidebar.markdown("### 🤖 Selecciona el modelo")
        self.llm = utils.configure_llm(key_suffix="_sidebar")

        # Luego mostrar instrucciones específicas para el chat con documentos
        with st.sidebar.expander("📜 Instrucciones de uso", expanded=True):
            st.markdown("""
            ### Cómo usar el Chat con Documentos

            1. **Sube tus documentos PDF** usando el selector de archivos abajo
            2. **Espera** a que se procesen los documentos
            3. **Haz preguntas** sobre el contenido de tus documentos
            4. **Revisa las fuentes** que aparecen debajo de cada respuesta

            #### Funcionalidades
            - Puedes subir **múltiples documentos** a la vez
            - El sistema usará **OCR** automáticamente si los PDFs no contienen texto legible
            - Las respuestas incluyen **referencias a las fuentes** de donde se extrajo la información

            #### Limitaciones
            - Documentos muy grandes pueden tardar más en procesarse
            - El OCR funciona mejor con documentos de buena calidad
            """)

        # Entradas del usuario en la barra lateral
        st.sidebar.markdown("### 📜 Cargar documentos")
        uploaded_files = st.sidebar.file_uploader(
            label="Selecciona archivos PDF", type=["pdf"], accept_multiple_files=True
        )

        # Mostrar información sobre los archivos cargados
        if uploaded_files:
            st.sidebar.success(f"✅ {len(uploaded_files)} archivo(s) cargado(s)")
            for file in uploaded_files:
                st.sidebar.info(f"📄 {file.name} ({round(file.size/1024, 1)} KB)")

        # Mostrar información del autor en la barra lateral (al final)
        try:
            from sidebar_info import show_author_info
            show_author_info()
        except ImportError:
            st.sidebar.warning("No se pudo cargar la información del autor.")

        # Verificar si hay archivos cargados
        if not uploaded_files:
            st.info(
                "👆 Por favor, carga documentos PDF en la barra lateral para comenzar."
            )
            st.stop()

        # 2. Mostrar mensajes del historial (saludo inicial y conversación)
        for msg in st.session_state["doc_chat_messages"]:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        # 3. Campo de entrada para nuevas preguntas (al final)
        user_query = st.chat_input(
            placeholder="¡Hazme una pregunta sobre tus documentos!"
        )

        if uploaded_files and user_query:
            try:
                # Añadir mensaje del usuario al historial
                st.session_state["doc_chat_messages"].append({"role": "user", "content": user_query})

                # Mostrar mensaje del usuario (se mostrará en la próxima ejecución)
                with st.chat_message("user"):
                    st.write(user_query)

                # Crear un contenedor para mostrar el estado del procesamiento
                processing_container = st.container()

                # Mostrar un mensaje de procesamiento
                with processing_container:
                    status_text = st.empty()
                    status_text.text("Procesando documentos y preparando respuesta...")

                    # Procesar documentos
                    qa_chain = self.setup_qa_chain(uploaded_files)

                    status_text.text("Procesando tu pregunta...")

                    # Generar respuesta
                    with st.chat_message("assistant"):
                        # Procesar la consulta en un contenedor oculto
                        with st.container():
                            # Crear un elemento vacío que no se mostrará al usuario
                            hidden_element = st.empty()
                            # Usar el StreamHandler con el elemento oculto
                            st_cb = StreamHandler(hidden_element)
                            # Invocar la cadena de QA
                            result = qa_chain.invoke(
                                {"question": user_query}, {"callbacks": [st_cb]}
                            )
                            # Obtener la respuesta
                            response = result["answer"]
                            # Limpiar el elemento oculto
                            hidden_element.empty()

                        # Mostrar la respuesta una sola vez
                        st.write(response)

                        # Añadir respuesta al historial
                        st.session_state["doc_chat_messages"].append(
                            {"role": "assistant", "content": response}
                        )

                        # Para mostrar referencias en un popover (no en expander)
                        st.markdown("**Fuentes de información:**")
                        for idx, doc in enumerate(result["source_documents"], 1):
                            try:
                                filename = os.path.basename(doc.metadata["source"])
                                page_num = doc.metadata["page"]
                                ref_title = f":blue[Referencia {idx}: *{filename} - página {page_num}*]"
                                with st.popover(ref_title):
                                    st.caption(doc.page_content)
                            except KeyError as e:
                                st.warning(
                                    f"No se pudo mostrar la referencia {idx}: Falta información en los metadatos."
                                )

                # Limpiar el contenedor de procesamiento
                processing_container.empty()

            except Exception as e:
                st.error(f"Error al procesar la consulta: {str(e)}")
                st.info("Intenta con una pregunta diferente o carga otros documentos.")


if __name__ == "__main__":
    obj = CustomDataChatbot()
    obj.main()

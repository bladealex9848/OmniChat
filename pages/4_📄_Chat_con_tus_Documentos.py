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
        self.llm = utils.configure_llm()

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
            st.error(
                "No se pudieron extraer fragmentos de texto de los documentos. Es posible que los PDFs no contengan texto legible."
            )
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
        
        # Mostrar información del autor en la barra lateral
        try:
            from sidebar_info import show_author_info
            show_author_info()
        except ImportError:
            st.sidebar.warning("No se pudo cargar la información del autor.")
        
        # Entradas del usuario en la barra lateral
        uploaded_files = st.sidebar.file_uploader(
            label="Cargar archivos PDF", type=["pdf"], accept_multiple_files=True
        )
        if not uploaded_files:
            st.info(
                "👆 Por favor, carga documentos PDF en la barra lateral para comenzar."
            )
            st.stop()

        # Mostrar información sobre los archivos cargados
        st.sidebar.success(f"✅ {len(uploaded_files)} archivo(s) cargado(s)")
        for file in uploaded_files:
            st.sidebar.info(f"📄 {file.name} ({round(file.size/1024, 1)} KB)")
        
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
                
                # Mostrar un mensaje de procesamiento
                with st.status(
                    "Procesando documentos y preparando respuesta...", expanded=True
                ) as status:
                    status.update(label="Analizando documentos PDF...", state="running")
                    qa_chain = self.setup_qa_chain(uploaded_files)

                    status.update(label="Procesando tu pregunta...", state="running")
                    
                    # Generar respuesta
                    with st.chat_message("assistant"):
                        st_cb = StreamHandler(st.empty())
                        result = qa_chain.invoke(
                            {"question": user_query}, {"callbacks": [st_cb]}
                        )
                        response = result["answer"]
                        
                        # Añadir respuesta al historial
                        st.session_state["doc_chat_messages"].append(
                            {"role": "assistant", "content": response}
                        )
                        
                        # Para mostrar referencias en un expander contraído
                        with st.expander("Fuentes de información", expanded=False):
                            st.markdown("### Fuentes de información")
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

                    status.update(
                        label="¡Respuesta generada con éxito!", state="complete"
                    )
            except Exception as e:
                st.error(f"Error al procesar la consulta: {str(e)}")
                st.info("Intenta con una pregunta diferente o carga otros documentos.")


if __name__ == "__main__":
    obj = CustomDataChatbot()
    obj.main()

import os
import sys

# Añadir el directorio raíz al path para poder importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils
import streamlit as st
from streaming import StreamHandler

from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

st.set_page_config(page_title="ChatPDF", page_icon="📄")
st.title("Chatea con tus documentos (RAG Básico)")
st.write(
    "Tiene acceso a documentos personalizados y puede responder a las consultas de los usuarios refiriéndose al contenido de esos documentos"
)


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

    @st.spinner("Analizando documentos..")
    def setup_qa_chain(self, uploaded_files):
        # Cargar documentos
        docs = []
        for file in uploaded_files:
            file_path = self.save_file(file)
            loader = PyPDFLoader(file_path)
            docs.extend(loader.load())

        # Dividir documentos
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )
        splits = text_splitter.split_documents(docs)

        # Crear embeddings y almacenar en vectordb
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        vectordb = FAISS.from_documents(splits, embeddings)

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

    @utils.enable_chat_history
    def main(self):
        # Entradas del usuario
        uploaded_files = st.sidebar.file_uploader(
            label="Cargar archivos PDF", type=["pdf"], accept_multiple_files=True
        )
        if not uploaded_files:
            st.error("¡Por favor, carga documentos PDF para continuar!")
            st.stop()

        user_query = st.chat_input(placeholder="¡Hazme una pregunta!")

        if uploaded_files and user_query:
            qa_chain = self.setup_qa_chain(uploaded_files)

            utils.display_msg(user_query, "user")

            with st.chat_message("assistant"):
                st_cb = StreamHandler(st.empty())
                result = qa_chain.invoke(
                    {"question": user_query}, {"callbacks": [st_cb]}
                )
                response = result["answer"]
                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )

                # Para mostrar referencias
                for idx, doc in enumerate(result["source_documents"], 1):
                    filename = os.path.basename(doc.metadata["source"])
                    page_num = doc.metadata["page"]
                    ref_title = (
                        f":blue[Reference {idx}: *{filename} - page.{page_num}*]"
                    )
                    with st.popover(ref_title):
                        st.caption(doc.page_content)


if __name__ == "__main__":
    obj = CustomDataChatbot()
    obj.main()

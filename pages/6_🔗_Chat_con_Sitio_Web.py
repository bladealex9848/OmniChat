import os
import utils
import requests
import traceback
import validators
import streamlit as st
from streaming import StreamHandler

from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

from langchain_core.documents.base import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain_community.embeddings import HuggingFaceEmbeddings

# Encabezado en Español
st.set_page_config(page_title="ChatWebsite", page_icon="🔗")
st.title('Chatea con Sitios Web')
st.write('Permite al chatbot interactuar con el contenido de los sitios web.')

class ChatbotWeb:

    def __init__(self):
        utils.sync_st_session()
        self.llm = utils.configure_llm()

    def scrape_website(self, url):
        content = ""
        try:
            base_url = "https://r.jina.ai/"
            final_url = base_url + url
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0'
            }
            response = requests.get(final_url, headers=headers)
            content = response.text
        except Exception as e:
            traceback.print_exc()
        return content

    def setup_vectordb(self, websites):
        # Cargar y analizar documentos
        docs = []
        for url in websites:
            docs.append(Document(
                page_content=self.scrape_website(url),
                metadata={"source":url}
            ))

        # Dividir documentos
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        splits = text_splitter.split_documents(docs)

        # Crear incrustaciones y almacenar en vectordb
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vectordb = DocArrayInMemorySearch.from_documents(splits, embeddings)
        return vectordb

    def setup_qa_chain(self, vectordb):
        # Definir recuperador
        retriever = vectordb.as_retriever(
            search_type='mmr',
            search_kwargs={'k':2, 'fetch_k':4}
        )

        # Configurar memoria para conversación contextual
        memory = ConversationBufferMemory(
            memory_key='chat_history',
            output_key='answer',
            return_messages=True
        )

        # Configurar cadena de QA
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=memory,
            return_source_documents=True,
            verbose=True
        )
        return qa_chain

    @utils.enable_chat_history
    def main(self):
        # Entradas del usuario
        if "websites" not in st.session_state:
            st.session_state["websites"] = []

        web_url = st.sidebar.text_area(
            label='Introduce la URL del sitio web',
            placeholder="https://",
            help="Para añadir otro sitio web, modifica este campo después de añadir el sitio web."
        )
        if st.sidebar.button(":heavy_plus_sign: Añadir Sitio Web"):
            valid_url = web_url.startswith('http') and validators.url(web_url)
            if not valid_url:
                st.sidebar.error("¡URL inválida! Por favor, revisa la URL del sitio web que has introducido.", icon="⚠️")
            else:
                st.session_state["websites"].append(web_url)

        if st.sidebar.button("Limpiar", type="primary"):
            st.session_state["websites"] = []
        
        websites = list(set(st.session_state["websites"]))

        if not websites:
            st.error("¡Por favor, introduce la URL del sitio web para continuar!")
            st.stop()
        else:
            st.sidebar.info("Sitios Web - \n - {}".format('\n - '.join(websites)))

            vectordb = self.setup_vectordb(websites)
            qa_chain = self.setup_qa_chain(vectordb)

            user_query = st.chat_input(placeholder="¡Hazme una pregunta!")
            if websites and user_query:
                utils.display_msg(user_query, 'user')

                with st.chat_message("assistant"):
                    st_cb = StreamHandler(st.empty())
                    result = qa_chain.invoke(
                        {"question":user_query},
                        {"callbacks": [st_cb]}
                    )
                    response = result["answer"]
                    st.session_state.messages.append({"role": "assistant", "content": response})

                    # Para mostrar referencias
                    for idx, doc in enumerate(result['source_documents'],1):
                        url = os.path.basename(doc.metadata['source'])
                        ref_title = f":blue[Referencia {idx}: *{url}*]"
                        with st.popover(ref_title):
                            st.caption(doc.page_content)

if __name__ == "__main__":
    obj = ChatbotWeb()
    obj.main()
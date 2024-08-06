import os
import utils
import requests
import traceback
import validators
import streamlit as st
from streaming import StreamHandler
from bs4 import BeautifulSoup

from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

from langchain_core.documents.base import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain_huggingface import HuggingFaceEmbeddings

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
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer texto de párrafos, encabezados y otros elementos relevantes
            for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'div', 'span']):
                content += element.get_text() + "\n"
            
        except Exception as e:
            st.error(f"Error al obtener contenido de {url}: {str(e)}")
            traceback.print_exc()
        return content

    def setup_vectordb(self, websites):
        docs = []
        for url in websites:
            content = self.scrape_website(url)
            if content:
                docs.append(Document(page_content=content, metadata={"source": url}))
            else:
                st.warning(f"No se pudo obtener contenido de {url}")

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)

        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vectordb = DocArrayInMemorySearch.from_documents(splits, embeddings)
        return vectordb

    def setup_qa_chain(self, vectordb):
        retriever = vectordb.as_retriever(search_type='mmr', search_kwargs={'k':2, 'fetch_k':4})
        memory = ConversationBufferMemory(memory_key='chat_history', output_key='answer', return_messages=True)
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
        if "websites" not in st.session_state:
            st.session_state["websites"] = []

        web_url = st.sidebar.text_input(
            label='Introduce la URL del sitio web',
            placeholder="https://ejemplo.com",
            help="Introduce la URL completa, incluyendo https://"
        )
        if st.sidebar.button(":heavy_plus_sign: Añadir Sitio Web"):
            if validators.url(web_url):
                st.session_state["websites"].append(web_url)
            else:
                st.sidebar.error("¡URL inválida! Por favor, introduce una URL completa y válida.", icon="⚠️")

        if st.sidebar.button("Limpiar", type="primary"):
            st.session_state["websites"] = []
        
        websites = list(set(st.session_state["websites"]))

        if not websites:
            st.error("¡Por favor, introduce al menos una URL de sitio web para continuar!")
            st.stop()
        else:
            st.sidebar.info("Sitios Web:\n" + "\n".join([f"- {url}" for url in websites]))

            with st.spinner("Procesando sitios web..."):
                vectordb = self.setup_vectordb(websites)
            qa_chain = self.setup_qa_chain(vectordb)

            user_query = st.chat_input(placeholder="¡Hazme una pregunta sobre los sitios web!")
            if user_query:
                utils.display_msg(user_query, 'user')

                with st.chat_message("assistant"):
                    st_cb = StreamHandler(st.empty())
                    result = qa_chain.invoke(
                        {"question": user_query},
                        {"callbacks": [st_cb]}
                    )
                    response = result["answer"]
                    st.session_state.messages.append({"role": "assistant", "content": response})

                    for idx, doc in enumerate(result['source_documents'], 1):
                        url = doc.metadata['source']
                        ref_title = f":blue[Referencia {idx}: *{url}*]"
                        with st.expander(ref_title):
                            st.write(doc.page_content)

if __name__ == "__main__":
    obj = ChatbotWeb()
    obj.main()
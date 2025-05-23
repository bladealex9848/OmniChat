import os
import sys
import time
import random
import json
import logging
from typing import List, Dict, Any, Optional

# Añadir el directorio raíz al path para poder importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils
import requests
import traceback
import validators
import streamlit as st
from streaming import StreamHandler
from bs4 import BeautifulSoup

# Importar funciones de búsqueda
from search_utils import get_search_tool, FallbackSearchTool

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

from langchain_core.documents.base import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import DocArrayInMemorySearch

# Intentar importar HuggingFaceEmbeddings con manejo de errores
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    # Fallback a embeddings de OpenAI si no está disponible HuggingFace
    from langchain_openai import OpenAIEmbeddings as HuggingFaceEmbeddings
    st.warning("No se pudo cargar HuggingFaceEmbeddings. Usando OpenAIEmbeddings como alternativa.")

# Configuración de la página (debe ser la primera llamada a Streamlit)
st.set_page_config(page_title="ChatWebsite", page_icon="🔗")

# Inicializar mensajes si no existen
if "website_chat_messages" not in st.session_state:
    st.session_state["website_chat_messages"] = [
        {
            "role": "assistant",
            "content": "Hola, soy un asistente virtual. ¿En qué puedo ayudarte hoy?",
        }
    ]

class ChatbotWeb:

    def __init__(self):
        utils.sync_st_session()
        self.llm = None
        self.use_search = False  # Por defecto, no usar búsqueda web

    def scrape_website(self, url):
        content = ""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, "html.parser")

            # Extraer texto de párrafos, encabezados y otros elementos relevantes
            for element in soup.find_all(["p", "h1", "h2", "h3", "div", "span"]):
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

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )
        splits = text_splitter.split_documents(docs)

        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        vectordb = DocArrayInMemorySearch.from_documents(splits, embeddings)
        return vectordb

    def perform_web_search(self, query):
        """Realiza una búsqueda web utilizando el sistema de respaldo automático"""
        try:
            with st.spinner("Buscando información en internet..."):
                # Obtener la herramienta de búsqueda con respaldo
                search_tool = get_search_tool()

                # Realizar la búsqueda
                results_text = search_tool.run(query)

                if results_text:
                    # Convertir el texto de resultados a formato de lista de diccionarios
                    results = []
                    sections = results_text.split('###')[1:] # Ignorar el texto antes del primer ###

                    for i, section in enumerate(sections, 1):
                        if not section.strip():
                            continue

                        lines = section.strip().split('\n')
                        title = lines[0].strip()

                        # Extraer snippet y URL
                        snippet = ''
                        link = ''

                        for line in lines[1:]:
                            if line.startswith('Fuente:'):
                                link = line.replace('Fuente:', '').strip()
                            else:
                                snippet += line + ' '

                        results.append({
                            "title": title,
                            "link": link,
                            "snippet": snippet.strip(),
                            "service": "Sistema de búsqueda con respaldo"
                        })

                    st.success(f"Búsqueda realizada con éxito usando el sistema de respaldo automático")
                    return results
                else:
                    st.warning("No se encontraron resultados en la búsqueda web.")
                    return []
        except Exception as e:
            logger.error(f"Error al realizar búsqueda web: {str(e)}")
            st.error(f"Error al realizar búsqueda web: {str(e)}")
            return []

    def format_search_results(self, results):
        """Formatea los resultados de búsqueda en un texto legible"""
        if not results:
            return "No se encontraron resultados."

        formatted_text = ""
        for i, result in enumerate(results, 1):
            formatted_text += f"### {i}. {result['title']}\n"
            formatted_text += f"{result['snippet']}\n"
            formatted_text += f"**Fuente:** [{result['link']}]({result['link']})\n\n"

        return formatted_text

    def setup_qa_chain(self, vectordb):
        retriever = vectordb.as_retriever(
            search_type="mmr", search_kwargs={"k": 2, "fetch_k": 4}
        )
        memory = ConversationBufferMemory(
            memory_key="chat_history", output_key="answer", return_messages=True
        )
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
        st.title("Chatea con Sitios Web y Búsqueda")
        st.write("Permite al chatbot interactuar con el contenido de sitios web y realizar búsquedas en internet.")

        # Inicializar la lista de sitios web si no existe
        if "websites" not in st.session_state:
            st.session_state["websites"] = []

        # Primero configurar el LLM en la barra lateral
        st.sidebar.markdown("### 🤖 Selecciona el modelo")
        self.llm = utils.configure_llm(key_suffix="_sidebar")

        # Opción para habilitar/deshabilitar búsqueda web
        st.sidebar.markdown("### Opciones de búsqueda")
        self.use_search = st.sidebar.checkbox(
            "Habilitar búsqueda en internet",
            value=False,
            help="Permite al chatbot buscar información en internet usando múltiples servicios de búsqueda"
        )

        # Mostrar información sobre los servicios de búsqueda disponibles
        if self.use_search:
            with st.sidebar.expander("Servicios de búsqueda disponibles"):
                st.markdown("""
                **Servicios de búsqueda (en orden de prioridad):**
                1. Google Programmable Search Engine
                2. Exa Search API
                3. YOU.com API
                4. Tavily API
                5. DuckDuckGo (fallback)

                El sistema intentará usar estos servicios en orden hasta obtener resultados.
                """)

        # Configuración de sitios web
        st.sidebar.markdown("### Sitios Web")
        web_url = st.sidebar.text_input(
            label="Introduce la URL del sitio web",
            placeholder="https://ejemplo.com",
            help="Introduce la URL completa, incluyendo https://",
        )
        if st.sidebar.button(":heavy_plus_sign: Añadir Sitio Web"):
            if validators.url(web_url):
                st.session_state["websites"].append(web_url)
            else:
                st.sidebar.error(
                    "¡URL inválida! Por favor, introduce una URL completa y válida.",
                    icon="⚠️",
                )

        if st.sidebar.button("Limpiar sitios", type="primary"):
            st.session_state["websites"] = []

        websites = list(set(st.session_state["websites"]))

        # Mostrar sitios web añadidos
        if websites:
            st.sidebar.info(
                "Sitios Web:\n" + "\n".join([f"- {url}" for url in websites])
            )

        # Mostrar información del autor en la barra lateral (al final)
        try:
            from sidebar_info import show_author_info
            show_author_info()
        except ImportError:
            st.sidebar.warning("No se pudo cargar la información del autor.")

        # Verificar si hay sitios web o si la búsqueda está habilitada
        if not websites and not self.use_search:
            st.error(
                "¡Por favor, introduce al menos una URL de sitio web o habilita la búsqueda en internet!"
            )
            st.stop()

        # Preparar el sistema de QA si hay sitios web
        qa_chain = None
        if websites:
            with st.spinner("Procesando sitios web..."):
                vectordb = self.setup_vectordb(websites)
                qa_chain = self.setup_qa_chain(vectordb)
        elif self.use_search:
            st.info("Modo de búsqueda en internet activado. No se han añadido sitios web.")

        # 2. Mostrar mensajes del historial (saludo inicial y conversación)
        for msg in st.session_state["website_chat_messages"]:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        # 3. Campo de entrada para nuevas preguntas (al final)
        placeholder = "¡Hazme una pregunta!" if self.use_search else "¡Hazme una pregunta sobre los sitios web!"
        user_query = st.chat_input(placeholder=placeholder)

        if user_query:
            # Añadir mensaje del usuario al historial
            st.session_state["website_chat_messages"].append({"role": "user", "content": user_query})

            # Mostrar mensaje del usuario (se mostrará en la próxima ejecución)
            with st.chat_message("user"):
                st.write(user_query)

            # Crear un contenedor para mostrar el estado del procesamiento
            processing_container = st.container()

            # Generar respuesta
            with st.chat_message("assistant"):
                # Procesar según el modo (búsqueda web, sitios web o híbrido)
                if self.use_search and (not websites or qa_chain is None):
                    # Modo de búsqueda web
                    with processing_container:
                        search_results = self.perform_web_search(user_query)

                    if search_results:
                        # Formatear resultados para mostrarlos
                        formatted_results = self.format_search_results(search_results)

                        # Construir prompt para el LLM con los resultados de búsqueda
                        prompt = f"""Basado en la siguiente información de búsqueda, responde a la pregunta del usuario.

                        Pregunta: {user_query}

                        Información de búsqueda:
                        {formatted_results}

                        Responde de manera concisa y clara, citando las fuentes cuando sea relevante.
                        """

                        # Procesar la consulta en un contenedor oculto
                        with st.container():
                            # Crear un elemento vacío que no se mostrará al usuario
                            hidden_element = st.empty()
                            # Usar el StreamHandler con el elemento oculto
                            st_cb = StreamHandler(hidden_element)
                            # Invocar el LLM
                            response = self.llm.invoke(prompt, streaming=True, callbacks=[st_cb])
                            # Limpiar el elemento oculto
                            hidden_element.empty()

                        # Mostrar la respuesta una sola vez
                        st.write(response)

                        # Añadir respuesta al historial
                        st.session_state["website_chat_messages"].append(
                            {"role": "assistant", "content": response}
                        )

                        # Mostrar fuentes de información en popovers
                        st.markdown("**Fuentes de información:**")
                        for idx, result in enumerate(search_results, 1):
                            service = result.get("service", "Búsqueda web")
                            ref_title = f":blue[Fuente {idx}: *{result['title']}* ({service})]"
                            with st.popover(ref_title):
                                st.markdown(f"**Extracto:** {result['snippet']}")
                                st.markdown(f"**URL:** [{result['link']}]({result['link']})")
                    else:
                        # Si no hay resultados de búsqueda
                        response = "Lo siento, no pude encontrar información relevante para tu pregunta. Por favor, intenta reformular tu consulta o añade sitios web específicos para obtener mejores resultados."
                        st.write(response)
                        st.session_state["website_chat_messages"].append(
                            {"role": "assistant", "content": response}
                        )

                # Modo de sitios web (usando qa_chain)
                elif websites and qa_chain is not None:
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
                    st.session_state["website_chat_messages"].append(
                        {"role": "assistant", "content": response}
                    )

                    # Mostrar referencias a sitios web en popovers
                    st.markdown("**Fuentes de sitios web:**")
                    for idx, doc in enumerate(result["source_documents"], 1):
                        url = doc.metadata["source"]
                        ref_title = f":blue[Referencia {idx}: *{url}*]"
                        with st.popover(ref_title):
                            st.caption(doc.page_content)

                # Modo híbrido: sitios web + búsqueda
                elif self.use_search and websites and qa_chain is not None:
                    # Primero intentar con los sitios web
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

                    # Si la respuesta es vaga o indica falta de información, complementar con búsqueda web
                    if "no tengo suficiente información" in response.lower() or "no puedo responder" in response.lower():
                        with processing_container:
                            st.info("Complementando con búsqueda en internet...")
                            search_results = self.perform_web_search(user_query)

                        if search_results:
                            formatted_results = self.format_search_results(search_results)
                            prompt = f"""Basado en la siguiente información adicional de búsqueda, mejora tu respuesta a la pregunta del usuario.

                            Pregunta: {user_query}

                            Tu respuesta inicial: {response}

                            Información adicional de búsqueda:
                            {formatted_results}

                            Proporciona una respuesta mejorada y más completa.
                            """

                            # Procesar en un contenedor oculto
                            with st.container():
                                improved_response = self.llm.invoke(prompt)
                                response = improved_response

                            # Mostrar fuentes de búsqueda web
                            st.markdown("**Fuentes adicionales de internet:**")
                            for idx, result in enumerate(search_results, 1):
                                service = result.get("service", "Búsqueda web")
                                ref_title = f":blue[Fuente adicional {idx}: *{result['title']}* ({service})]"
                                with st.popover(ref_title):
                                    st.markdown(f"**Extracto:** {result['snippet']}")
                                    st.markdown(f"**URL:** [{result['link']}]({result['link']})")

                    # Mostrar la respuesta una sola vez
                    st.write(response)

                    # Añadir respuesta al historial
                    st.session_state["website_chat_messages"].append(
                        {"role": "assistant", "content": response}
                    )

                    # Mostrar referencias a sitios web
                    st.markdown("**Fuentes de sitios web:**")
                    for idx, doc in enumerate(result["source_documents"], 1):
                        url = doc.metadata["source"]
                        ref_title = f":blue[Referencia {idx}: *{url}*]"
                        with st.popover(ref_title):
                            st.caption(doc.page_content)

            # Limpiar el contenedor de procesamiento
            processing_container.empty()


if __name__ == "__main__":
    obj = ChatbotWeb()
    obj.main()

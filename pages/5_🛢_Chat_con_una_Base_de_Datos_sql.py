import sys
import os

# Añadir el directorio raíz al path para poder importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils
import sqlite3
import streamlit as st
from pathlib import Path
from sqlalchemy import create_engine
from urllib.parse import quote_plus
import pymysql

from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_community.utilities.sql_database import SQLDatabase

# Configuración de la página
st.set_page_config(page_title="ChatSQL", page_icon="🛢")

# Inicializar mensajes si no existen
if "sql_chat_messages" not in st.session_state:
    st.session_state["sql_chat_messages"] = [
        {
            "role": "assistant",
            "content": "Hola, soy un asistente virtual. ¿En qué puedo ayudarte hoy?",
        }
    ]

class SqlChatbot:

    def __init__(self):
        utils.sync_st_session()
        try:
            self.llm = utils.configure_llm()
        except Exception as e:
            st.error(f"Error al configurar el modelo de lenguaje: {str(e)}")
            st.stop()

    def setup_db(self, connection_info):
        try:
            if connection_info == "USE_SAMPLE_DB":
                db_filepath = (
                    Path(__file__).parent.parent / "assets/Chinook.db"
                ).absolute()
                db_uri = f"sqlite:////{db_filepath}"
                creator = lambda: sqlite3.connect(
                    f"file:{db_filepath}?mode=ro", uri=True
                )
                db = SQLDatabase(create_engine("sqlite:///", creator=creator))
            elif isinstance(connection_info, dict):
                # Construir la URI a partir de los datos del formulario
                db_uri = f"mysql+pymysql://{connection_info['user']}:{quote_plus(connection_info['password'])}@{connection_info['host']}:{connection_info['port']}/{connection_info['database']}"
                engine = create_engine(db_uri)
                db = SQLDatabase(engine)
            else:
                # Parsear la URI de conexión manualmente
                parts = connection_info.split("://")
                if len(parts) != 2:
                    raise ValueError("Formato de URI de base de datos inválido")

                scheme, rest = parts
                user_pass, host_db = rest.split("@", 1)
                user, password = user_pass.split(":", 1)

                # Codificar la contraseña correctamente
                encoded_password = quote_plus(password)

                # Reconstruir la URI con la contraseña codificada y usar pymysql
                encoded_uri = f"mysql+pymysql://{user}:{encoded_password}@{host_db}"

                # Crear el engine con la URI codificada
                engine = create_engine(encoded_uri)
                db = SQLDatabase(engine)

            with st.sidebar.expander("Tablas de la base de datos", expanded=True):
                st.info("\n- " + "\n- ".join(db.get_usable_table_names()))
            return db
        except Exception as e:
            st.error(f"Error al configurar la base de datos: {str(e)}")
            return None

    def setup_sql_agent(self, db):
        try:
            agent = create_sql_agent(
                llm=self.llm,
                db=db,
                top_k=10,
                verbose=True,
                agent_type="openai-tools",
                handle_parsing_errors=True,
                handle_sql_errors=True,
            )
            return agent
        except Exception as e:
            st.error(f"Error al crear el agente SQL: {str(e)}")
            return None

    def main(self):
        # 1. Título y subtítulo (siempre visible en la parte superior)
        st.title("Chatea con base de datos SQL")
        st.write(
            "Permite al chatbot interactuar con una base de datos SQL a través de comandos simples y conversacionales."
        )

        # Mostrar información del autor e instrucciones en la barra lateral
        try:
            from sidebar_info import show_author_info

            # Instrucciones específicas para el chat con base de datos SQL
            instrucciones = """
            ### 🔎 Cómo usar el Chat con Base de Datos SQL

            1. **Selecciona una base de datos**:
               - Usa la base de datos de ejemplo (Chinook)
               - O conecta a tu propia base de datos SQL

            2. **Explora las tablas** disponibles en el panel lateral

            3. **Haz preguntas** sobre los datos en lenguaje natural
               - "Muestra todos los clientes de USA"
               - "Cuáles son las 5 canciones más vendidas?"
               - "Calcula el total de ventas por país"

            #### Funcionalidades
            - Traduce lenguaje natural a consultas SQL
            - Muestra resultados en formato tabular
            - Soporta análisis complejos y agregaciones

            #### Limitaciones
            - Las consultas muy complejas pueden requerir reformulación
            - Por seguridad, solo se permiten operaciones de lectura
            """

            show_author_info(show_instructions=True,
                           instructions_title="🔎 Instrucciones",
                           instructions_content=instrucciones)
        except ImportError:
            st.sidebar.warning("No se pudo cargar la información del autor.")

        radio_opt = [
            "Usar base de datos de ejemplo - Chinook.db",
            "Conectar a tu base de datos SQL",
        ]
        selected_opt = st.sidebar.radio(
            label="Elige la opción adecuada", options=radio_opt
        )

        connection_info = "USE_SAMPLE_DB"
        if radio_opt.index(selected_opt) == 1:
            with st.sidebar.popover(
                ":orange[⚠️ Nota de seguridad]", use_container_width=True
            ):
                warning = "Construir sistemas de preguntas y respuestas de bases de datos SQL requiere ejecutar consultas SQL generadas por el modelo. Hay riesgos inherentes en hacer esto. Asegúrese de que los permisos de conexión a la base de datos estén siempre tan limitados como sea posible para las necesidades de su cadena/agente.\n\nPara obtener más información sobre las mejores prácticas de seguridad en general - [lea esto](https://python.langchain.com/docs/security)."
                st.warning(warning)

            connection_method = st.sidebar.radio("Método de conexión", ["Formulario"])

            if connection_method == "URL":
                connection_info = st.sidebar.text_input(
                    label="Database URI",
                    placeholder="mysql://user:pass@hostname:port/db",
                )
            else:
                connection_info = {
                    "host": st.sidebar.text_input("Host", "localhost"),
                    "port": st.sidebar.text_input("Puerto", "3306"),
                    "user": st.sidebar.text_input("Usuario", "root"),
                    "password": st.sidebar.text_input("Contraseña", type="password"),
                    "database": st.sidebar.text_input("Nombre de la base de datos"),
                }

        if not connection_info:
            st.error("¡Por favor, introduce la información de conexión para continuar!")
            st.stop()

        db = self.setup_db(connection_info)
        if db is None:
            st.stop()

        agent = self.setup_sql_agent(db)
        if agent is None:
            st.stop()

        # 2. Mostrar mensajes del historial (saludo inicial y conversación)
        for msg in st.session_state["sql_chat_messages"]:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        # 3. Campo de entrada para nuevas preguntas (al final)
        user_query = st.chat_input(placeholder="¡Hazme una pregunta!")

        if user_query:
            # Añadir mensaje del usuario al historial
            st.session_state["sql_chat_messages"].append({"role": "user", "content": user_query})

            # Mostrar mensaje del usuario (se mostrará en la próxima ejecución)
            with st.chat_message("user"):
                st.write(user_query)

            # Generar respuesta
            with st.chat_message("assistant"):
                st_cb = StreamlitCallbackHandler(st.container())
                try:
                    result = agent.invoke({"input": user_query}, {"callbacks": [st_cb]})
                    response = result["output"]

                    # Añadir respuesta al historial
                    st.session_state["sql_chat_messages"].append(
                        {"role": "assistant", "content": response}
                    )
                    st.write(response)
                except Exception as e:
                    st.error(f"Error al procesar la consulta: {str(e)}")


if __name__ == "__main__":
    try:
        obj = SqlChatbot()
        obj.main()
    except Exception as e:
        st.error(f"Error inesperado: {str(e)}")

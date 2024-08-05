import utils
import sqlite3
import streamlit as st
from pathlib import Path
from sqlalchemy import create_engine
from urllib.parse import quote_plus

from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_community.utilities.sql_database import SQLDatabase

# Configuración de la página
st.set_page_config(page_title="ChatSQL", page_icon="🛢")
st.title('Chatea con base de datos SQL')
st.write('Permite al chatbot interactuar con una base de datos SQL a través de comandos simples y conversacionales.')

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
            if connection_info == 'USE_SAMPLE_DB':
                db_filepath = (Path(__file__).parent.parent / "assets/Chinook.db").absolute()
                db_uri = f"sqlite:////{db_filepath}"
                creator = lambda: sqlite3.connect(f"file:{db_filepath}?mode=ro", uri=True)
                db = SQLDatabase(create_engine("sqlite:///", creator=creator))
            elif isinstance(connection_info, dict):
                # Construir la URI a partir de los datos del formulario
                db_uri = f"mysql://{connection_info['user']}:{quote_plus(connection_info['password'])}@{connection_info['host']}:{connection_info['port']}/{connection_info['database']}"
                engine = create_engine(db_uri)
                db = SQLDatabase(engine)
            else:
                # Parsear la URI de conexión manualmente
                parts = connection_info.split('://')
                if len(parts) != 2:
                    raise ValueError("Formato de URI de base de datos inválido")
                
                scheme, rest = parts
                user_pass, host_db = rest.split('@', 1)
                user, password = user_pass.split(':', 1)
                
                # Codificar la contraseña correctamente
                encoded_password = quote_plus(password)
                
                # Reconstruir la URI con la contraseña codificada
                encoded_uri = f"{scheme}://{user}:{encoded_password}@{host_db}"
                
                # Crear el engine con la URI codificada
                engine = create_engine(encoded_uri)
                db = SQLDatabase(engine)
            
            with st.sidebar.expander('Tablas de la base de datos', expanded=True):
                st.info('\n- '+'\n- '.join(db.get_usable_table_names()))
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
                handle_sql_errors=True
            )
            return agent
        except Exception as e:
            st.error(f"Error al crear el agente SQL: {str(e)}")
            return None

    @utils.enable_chat_history
    def main(self):
        radio_opt = ['Usar base de datos de ejemplo - Chinook.db', 'Conectar a tu base de datos SQL']
        selected_opt = st.sidebar.radio(
            label='Elige la opción adecuada',
            options=radio_opt
        )
        
        connection_info = 'USE_SAMPLE_DB'
        if radio_opt.index(selected_opt) == 1:
            with st.sidebar.popover(':orange[⚠️ Nota de seguridad]', use_container_width=True):
                warning = "Construir sistemas de preguntas y respuestas de bases de datos SQL requiere ejecutar consultas SQL generadas por el modelo. Hay riesgos inherentes en hacer esto. Asegúrese de que los permisos de conexión a la base de datos estén siempre tan limitados como sea posible para las necesidades de su cadena/agente.\n\nPara obtener más información sobre las mejores prácticas de seguridad en general - [lea esto](https://python.langchain.com/docs/security)."
                st.warning(warning)
            
            connection_method = st.sidebar.radio("Método de conexión", ["Formulario"])
            
            if connection_method == "URL":
                connection_info = st.sidebar.text_input(
                    label='Database URI',
                    placeholder='mysql://user:pass@hostname:port/db'
                )
            else:
                connection_info = {
                    "host": st.sidebar.text_input("Host", "localhost"),
                    "port": st.sidebar.text_input("Puerto", "3306"),
                    "user": st.sidebar.text_input("Usuario", "root"),
                    "password": st.sidebar.text_input("Contraseña", type="password"),
                    "database": st.sidebar.text_input("Nombre de la base de datos")
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

        user_query = st.chat_input(placeholder="¡Hazme una pregunta!")

        if user_query:
            st.session_state.messages.append({"role": "user", "content": user_query})
            st.chat_message("user").write(user_query)

            with st.chat_message("assistant"):
                st_cb = StreamlitCallbackHandler(st.container())
                try:
                    result = agent.invoke(
                        {"input": user_query},
                        {"callbacks": [st_cb]}
                    )
                    response = result["output"]
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.write(response)
                except Exception as e:
                    st.error(f"Error al procesar la consulta: {str(e)}")

if __name__ == "__main__":
    try:
        obj = SqlChatbot()
        obj.main()
    except Exception as e:
        st.error(f"Error inesperado: {str(e)}")
# OmniChat: Asistente Virtual Todo en Uno

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/bladealex1844/OmniChat?quickstart=1)

OmniChat es un asistente virtual versátil desarrollado con Langchain y Streamlit. Aprovecha el poder de los Modelos de Lenguaje (LLMs) para ofrecer una amplia gama de funcionalidades, simplificando la interacción con diversos tipos de información y bases de datos.

## 💬 Funcionalidades de OmniChat

OmniChat ofrece las siguientes capacidades:

- **Chatbot Básico**: 
  Mantén conversaciones interactivas con el LLM.

- **Chatbot Consciente del Contexto**: 
  Un asistente que recuerda conversaciones previas y proporciona respuestas acordes.

- **Chat con Documentos**: 
  Permite al chatbot acceder a documentos personalizados, respondiendo preguntas basadas en la información contenida.

- **Chat con Base de Datos SQL**: 
  Interactúa con bases de datos SQL mediante comandos conversacionales simples.

- **Chat con Sitios Web**: 
  Permite al chatbot interactuar con contenidos de sitios web.

## <img src="https://streamlit.io/images/brand/streamlit-mark-color.png" width="40" height="22"> Aplicación Streamlit

OmniChat es una aplicación multi-página desarrollada con Streamlit, que incluye todas las funcionalidades mencionadas.

Accede a la aplicación aquí: [OmniChat en Streamlit](https://omnichat-ai.streamlit.app)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://omnichat-ai.streamlit.app)

## 🖥️ Ejecución Local

```
# Ejecutar la aplicación principal de Streamlit
$ streamlit run Inicio.py
```

## 📦 Ejecución con Docker
```
# Generar la imagen
$ docker build -t omnichat .
```

# Ejecutar el contenedor Docker
```
$ docker run -p 8501:8501 omnichat
```

## 💁 Contribuciones
Planeamos añadir más funcionalidades a OmniChat con el tiempo. Las contribuciones son bienvenidas.

## 📄 Licencia
Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para obtener más detalles.
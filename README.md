# OmniChat: Laboratorio de Herramientas de IA

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/bladealex1844/OmniChat?quickstart=1)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://omnichat-ai.streamlit.app)
![Visitantes](https://api.visitorbadge.io/api/visitors?path=https%3A%2F%2Fomnichat.streamlit.app&label=Visitantes&labelColor=%235d5d5d&countColor=%231e7ebf&style=flat)

## Tabla de Contenidos
1. [Descripción](#descripción)
2. [Características Principales](#características-principales)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Requisitos Previos](#requisitos-previos)
5. [Instalación](#instalación)
6. [Configuración](#configuración)
7. [Uso](#uso)
8. [Herramientas Disponibles](#herramientas-disponibles)
9. [Sistema de Búsqueda](#sistema-de-búsqueda)
10. [Arquitectura del Sistema](#arquitectura-del-sistema)
11. [Componentes Principales](#componentes-principales)
12. [Flujo de Trabajo](#flujo-de-trabajo)
13. [APIs y Servicios Integrados](#apis-y-servicios-integrados)
14. [Manejo de Errores y Logging](#manejo-de-errores-y-logging)
15. [Optimización y Caché](#optimización-y-caché)
16. [Contribución](#contribución)
17. [Licencia](#licencia)
18. [Contacto](#contacto)

## Descripción

OmniChat es un laboratorio completo de herramientas de Inteligencia Artificial que integra múltiples capacidades de procesamiento de lenguaje natural, visión por computadora y búsqueda web. Diseñado como una plataforma modular y extensible, OmniChat permite a los usuarios interactuar con diversos modelos de lenguaje y herramientas especializadas a través de una interfaz unificada y amigable.

El proyecto implementa una arquitectura flexible que facilita la integración de nuevos modelos y servicios, con un enfoque en la robustez, la eficiencia y la experiencia de usuario. OmniChat utiliza Streamlit como framework principal para su interfaz, lo que permite una rápida iteración y desarrollo de nuevas funcionalidades.

## Características Principales

### 1. Múltiples Interfaces de Chat
- **Chatbot Básico**: Interacción simple con modelos de lenguaje para consultas generales.
- **Chatbot con Memoria**: Un asistente que recuerda conversaciones previas y proporciona respuestas acordes.
- **Chatbot con Acceso a Internet**: Capacidad de responder preguntas sobre eventos actuales mediante búsqueda web.
- **Chat con Documentos**: Permite al chatbot acceder a documentos personalizados, respondiendo preguntas basadas en la información contenida.
- **Chat con Base de Datos SQL**: Interactúa con bases de datos SQL mediante comandos conversacionales simples.
- **Chat con Sitios Web**: Permite al chatbot interactuar con contenidos de sitios web.
- **Chat Multimodal**: Analiza imágenes y responde preguntas sobre ellas usando modelos multimodales gratuitos.
- **OCR con Mistral AI**: Extrae texto de imágenes y documentos PDF utilizando la API de OCR de Mistral AI.

### 2. Sistema de Búsqueda con Respaldo Automático
- **Múltiples Proveedores de Búsqueda**:
  - DuckDuckGo API como método principal
  - DuckDuckGo HTML como primer respaldo
  - Google PSE API como segundo respaldo
  - Exa API como tercer respaldo
- **Cambio Transparente**: Transición automática entre métodos cuando uno falla
- **Priorización de Métodos Gratuitos**: Uso de APIs pagas solo cuando es necesario
- **Manejo Robusto de Errores**: Recuperación automática ante fallos de API

### 3. Integración de Modelos de IA
- **Modelos de OpenAI**: Acceso a GPT-4o-mini y otros modelos
- **Modelos de OpenRouter**: Soporte para modelos multimodales gratuitos
- **Mistral AI**: Integración para OCR y procesamiento de documentos
- **Selección Flexible**: Interfaz para elegir entre diferentes modelos disponibles

### 4. Procesamiento de Documentos
- **OCR Avanzado**: Extracción de texto de imágenes y PDFs
- **Soporte para Múltiples Formatos**: PDF, JPG, PNG
- **Preservación de Estructura**: Mantiene el formato del texto extraído
- **Descarga de Resultados**: Exportación en múltiples formatos (TXT, JSON, Markdown)

### 5. Interfaz de Usuario Optimizada
- **Diseño Limpio y Moderno**: Interfaz intuitiva basada en Streamlit
- **Barra Lateral Informativa**: Acceso rápido a configuraciones y recursos
- **Visualización de Resultados**: Presentación clara de respuestas y datos
- **Experiencia Responsiva**: Adaptación a diferentes dispositivos y tamaños de pantalla

## Estructura del Proyecto

```
OmniChat/
│
├── Inicio.py                   # Punto de entrada principal y página de inicio
├── utils.py                    # Funciones de utilidad y configuración
├── sidebar_info.py             # Información de la barra lateral
├── streaming.py                # Manejo de streaming para respuestas de chat
├── search_services.py          # Servicios de búsqueda web con respaldo
├── custom_callbacks.py         # Callbacks personalizados para LangChain
│
├── pages/                      # Páginas de la aplicación
│   ├── 1_💬_Chatbot_Basico.py             # Chatbot simple
│   ├── 2_🧠_Chatbot_Memoria.py            # Chatbot con memoria de conversación
│   ├── 3_🌐_Chatbot_Acceso_Internet.py    # Chatbot con búsqueda web
│   ├── 4_📄_Chat_Documentos.py            # Chat con documentos
│   ├── 5_📊_Chat_SQL.py                   # Chat con bases de datos SQL
│   ├── 6_🔗_Chat_Sitios_Web.py            # Chat con sitios web
│   ├── 7_🖼️_Chat_Multimodal.py            # Chat con capacidades multimodales
│   └── 8_🔍_OCR_Mistral.py                # OCR con Mistral AI
│
├── .streamlit/                 # Configuración de Streamlit
│   ├── config.toml             # Configuración general de Streamlit
│   └── secrets.toml            # Almacenamiento seguro de claves API (no incluido en el repositorio)
│
├── assets/                     # Recursos estáticos
│   └── profile.jpg             # Imagen de perfil para la barra lateral
│
├── scripts/                    # Scripts de utilidad
│   ├── clean_cache.py          # Script para limpiar la caché de Python
│   ├── force_restart.py        # Script para reiniciar la aplicación
│   └── restart_app.py          # Script para reiniciar la aplicación de manera limpia
│
├── .gitignore                  # Archivos y directorios ignorados por Git
└── requirements.txt            # Dependencias de Python
```

## Requisitos Previos

- Python 3.8+
- Streamlit 1.44.0+
- Conexión a Internet (para búsqueda web y APIs externas)
- Claves API para servicios externos (opcional, según las funcionalidades que se deseen utilizar)

## Instalación

1. Clona el repositorio:
   ```
   git clone https://github.com/bladealex9848/OmniChat.git
   cd OmniChat
   ```

2. Crea y activa un entorno virtual:
   ```
   python -m venv venv
   source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
   ```

3. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

4. Configura tus claves API (opcional):
   Crea un archivo `.streamlit/secrets.toml` y añade tus claves API:
   ```toml
   OPENAI_API_KEY = "tu_clave_openai_aqui"
   MISTRAL_API_KEY = "tu_clave_mistral_aqui"
   OPENROUTER_API_KEY = "tu_clave_openrouter_aqui"
   GOOGLE_PSE_API_KEY = "tu_clave_google_pse_aqui"
   GOOGLE_PSE_ID = "tu_id_google_pse_aqui"
   EXA_API_KEY = "tu_clave_exa_aqui"
   TAVILY_API_KEY = "tu_clave_tavily_aqui"
   YOU_API_KEY = "tu_clave_you_aqui"
   ```

## Configuración

OmniChat está diseñado para funcionar con configuración mínima. Las principales opciones de configuración se encuentran en:

1. **Archivo `.streamlit/config.toml`**: Configuración general de la interfaz de Streamlit.
2. **Archivo `.streamlit/secrets.toml`**: Almacenamiento seguro de claves API.
3. **Interfaz de usuario**: Muchas opciones se pueden configurar directamente desde la barra lateral de la aplicación.

## Uso

Para iniciar la aplicación, ejecuta:
```
streamlit run Inicio.py
```

Luego, abre tu navegador y ve a `http://localhost:8501`.

La interfaz principal te permitirá:
1. Navegar entre las diferentes herramientas disponibles a través de la barra lateral.
2. Interactuar con los diferentes chatbots y herramientas.
3. Configurar opciones específicas para cada herramienta.
4. Ver información sobre el desarrollador y recursos útiles.

## Herramientas Disponibles

### 1. Chatbot Básico
Un chatbot simple que permite interactuar con modelos de lenguaje para consultas generales. Ideal para preguntas y respuestas básicas sin necesidad de contexto adicional.

### 2. Chatbot con Memoria
Una versión mejorada del chatbot básico que mantiene el contexto de la conversación, permitiendo referencias a mensajes anteriores y una experiencia más natural.

### 3. Chatbot con Acceso a Internet
Un chatbot potenciado con capacidad de búsqueda web, ideal para responder preguntas sobre eventos actuales, noticias recientes o información que requiere datos actualizados.

### 4. Chat con Documentos
Permite cargar documentos (PDF, TXT) y hacer preguntas sobre su contenido. El sistema analiza los documentos y proporciona respuestas basadas en la información contenida en ellos.

### 5. Chat con SQL
Interfaz conversacional para interactuar con bases de datos SQL. Permite realizar consultas en lenguaje natural que se traducen a SQL y ejecutan contra la base de datos.

### 6. Chat con Sitios Web
Permite analizar y extraer información de sitios web específicos, respondiendo preguntas basadas en el contenido de las páginas web.

### 7. Chat Multimodal
Chatbot con capacidad para procesar y analizar imágenes, utilizando modelos multimodales gratuitos de OpenRouter como Llama 4 Maverick/Scout y Qwen 2.5 VL.

### 8. OCR con Mistral AI
Herramienta especializada para extraer texto de imágenes y documentos PDF utilizando la API de OCR de Mistral AI, con preservación de la estructura del texto.

## Sistema de Búsqueda

OmniChat implementa un sistema de búsqueda web con respaldo automático y transparente:

### Métodos Gratuitos (Prioridad)
1. **DuckDuckGo API** (método principal)
2. **DuckDuckGo HTML** (respaldo gratuito)

### APIs como Respaldo
3. **Google PSE API** (primera API de respaldo)
4. **Exa API** (segunda API de respaldo)

El sistema cambia automáticamente entre métodos de búsqueda cuando uno falla, sin mostrar errores al usuario. Prioriza los métodos gratuitos y solo utiliza las APIs como respaldo si es necesario.

Si todos los métodos fallan, el sistema proporcionará una respuesta basada en información básica almacenada, indicando que puede no estar completamente actualizada.

## Arquitectura del Sistema

OmniChat utiliza una arquitectura modular basada en componentes, donde cada herramienta funciona como un módulo independiente pero integrado en la plataforma principal. La aplicación se construye sobre Streamlit, aprovechando su capacidad para crear interfaces interactivas rápidamente.

### Componentes Clave:
1. **Interfaz de Usuario**: Implementada con Streamlit para una experiencia interactiva y responsiva.
2. **Módulos de Chat**: Implementaciones específicas para diferentes tipos de chatbots y herramientas.
3. **Sistema de Búsqueda**: Arquitectura con múltiples proveedores y mecanismos de respaldo.
4. **Integración de APIs**: Conexiones a servicios externos como OpenAI, Mistral y OpenRouter.
5. **Utilidades Comunes**: Funciones compartidas para manejo de sesiones, streaming y configuración.

## Componentes Principales

### Inicio.py
- Punto de entrada principal de la aplicación.
- Implementa la página de inicio con información general.
- Configura la estructura básica de la interfaz.

### utils.py
- Contiene funciones de utilidad compartidas por múltiples componentes.
- Implementa la configuración de modelos de lenguaje.
- Proporciona decoradores y helpers para la interfaz de usuario.

### sidebar_info.py
- Gestiona la información mostrada en la barra lateral.
- Implementa la presentación de información del autor y enlaces útiles.

### search_services.py
- Implementa el sistema de búsqueda web con múltiples proveedores.
- Gestiona la lógica de respaldo y recuperación ante fallos.

### Páginas (directorio pages/)
- Cada archivo implementa una herramienta específica.
- Contienen clases que encapsulan la lógica de cada funcionalidad.
- Utilizan componentes comunes para mantener consistencia.

## Flujo de Trabajo

1. El usuario accede a la aplicación a través de la página principal.
2. Navega a la herramienta deseada utilizando la barra lateral.
3. Interactúa con la herramienta seleccionada (chat, carga de documentos, etc.).
4. La aplicación procesa las entradas del usuario y genera respuestas utilizando los modelos y servicios apropiados.
5. Los resultados se muestran en la interfaz de manera clara y organizada.
6. El usuario puede continuar la interacción o cambiar a otra herramienta según sus necesidades.

## APIs y Servicios Integrados

OmniChat integra varios servicios externos para proporcionar sus funcionalidades:

- **OpenAI**: Para modelos de lenguaje como GPT-4o-mini.
- **Mistral AI**: Para OCR y procesamiento de documentos.
- **OpenRouter**: Para acceso a modelos multimodales gratuitos.
- **Servicios de Búsqueda**: DuckDuckGo, Google PSE, Exa, etc.
- **LangChain**: Framework para integración de componentes de IA.

Cada servicio se configura y utiliza de manera modular, permitiendo añadir nuevos servicios o reemplazar los existentes con facilidad.

## Manejo de Errores y Logging

OmniChat implementa un sistema robusto de manejo de errores:

- **Mensajes de Error Informativos**: Guía clara para el usuario cuando ocurren problemas.
- **Recuperación Automática**: Mecanismos de respaldo para servicios que fallan.
- **Validación de Entradas**: Prevención de errores mediante validación previa.
- **Logging Estructurado**: Registro de eventos y errores para diagnóstico.

## Optimización y Caché

Para mejorar el rendimiento, OmniChat utiliza varias técnicas de optimización:

- **Caché de Sesión**: Almacenamiento de resultados frecuentes para reducir llamadas a APIs.
- **Inicialización Eficiente**: Uso de decoradores como `@st.cache_resource` para componentes pesados.
- **Carga Diferida**: Inicialización de recursos solo cuando son necesarios.
- **Streaming de Respuestas**: Presentación progresiva de respuestas largas para mejorar la experiencia de usuario.

## Contribución

Las contribuciones son bienvenidas. Por favor, sigue estos pasos:

1. Haz fork del repositorio.
2. Crea una nueva rama (`git checkout -b feature/NuevaFuncionalidad`).
3. Realiza tus cambios y haz commit (`git commit -m 'Añadir nueva funcionalidad'`).
4. Push a la rama (`git push origin feature/NuevaFuncionalidad`).
5. Abre un Pull Request.

### Git Hooks

Este proyecto incluye git hooks para validar el código antes de commit y push. Los hooks realizan las siguientes validaciones:

- Detectan claves API expuestas en el código
- Verifican que no haya archivos grandes (>10MB)
- Verifican que no haya conflictos de merge sin resolver
- Verifican que los archivos Python no tengan errores de sintaxis
- Verifican que requirements.txt y README.md estén actualizados

#### Instalación Local (solo para este repositorio)

Para instalar los hooks solo en este repositorio, ejecuta:

```bash
./scripts/install-git-hooks.sh
```

#### Instalación Global (para todos los repositorios)

Para instalar los hooks globalmente en tu sistema (afectará a todos los repositorios Git actuales y futuros), ejecuta:

```bash
./scripts/install-global-git-hooks.sh
```

Esto instalará los hooks en `~/.git-hooks/` y configurará Git para usar esta ubicación en todos los repositorios. **Solo necesitas ejecutar este script una vez en tu equipo**.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - vea el archivo [LICENSE](LICENSE) para más detalles.

## Contacto

Alexander Oviedo Fadul

[![GitHub](https://img.shields.io/badge/GitHub-Perfil-gray?logo=github&style=flat)](https://github.com/bladealex9848)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Perfil-blue?logo=linkedin&style=flat)](https://www.linkedin.com/in/alexanderoviedofadul/)
[![Web](https://img.shields.io/badge/Web-alexanderoviedofadul.dev-green?logo=web&style=flat)](https://alexanderoviedofadul.dev/)
[![Web](https://img.shields.io/badge/Web-Marduk.pro-green?logo=web&style=flat)](https://marduk.pro)
[![Email](https://img.shields.io/badge/Email-Contacto-red?logo=gmail&style=flat)](mailto:alexander.oviedo.fadul@gmail.com)
[![WhatsApp](https://img.shields.io/badge/WhatsApp-Contacto-25D366?logo=whatsapp&style=flat)](https://wa.me/573015930519)

"""
Módulo para mostrar información de autoría y enlaces en la barra lateral.
"""

import streamlit as st

def show_author_info():
    """
    Muestra información del autor y enlaces en la barra lateral.
    """
    # Separador
    st.sidebar.markdown("---")

    # Título de desarrollador
    st.sidebar.markdown("### 👨‍💻 Desarrollador")

    # Información del desarrollador con foto y nombre
    col1, col2 = st.sidebar.columns([1, 3])
    with col1:
        st.image("assets/profile.jpg", width=80)
    with col2:
        st.markdown("#### Alexander Oviedo Fadul")
        st.markdown("*Ingeniero de Sistemas & Desarrollador IA*")

    # Biografía breve
    st.sidebar.markdown("""
    Ingeniero de Sistemas con más de 10 años de experiencia en desarrollo de software y soluciones de IA.
    Especialista en aplicaciones web, automatización y análisis de datos.
    """)

    # Redes sociales y perfiles profesionales con etiquetas mejoradas
    st.sidebar.markdown("##### Perfiles Profesionales")

    # Estilo CSS para las etiquetas de enlaces inspirado en la etiqueta de visitantes
    st.markdown("""
    <style>
    .badge-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 10px;
        justify-content: center;
    }
    .badge-link {
        text-decoration: none;
        display: inline-block;
    }
    .badge {
        display: inline-flex;
        align-items: center;
        background-color: #f0f2f6;
        border-radius: 5px;
        padding: 5px 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.2s ease;
    }
    .badge:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .badge-label {
        font-weight: 500;
        color: #5d5d5d;
        margin-right: 5px;
    }
    .badge-value {
        font-weight: bold;
        color: #1e7ebf;
    }
    .badge-linkedin .badge-value {
        color: #0077B5;
    }
    .badge-github .badge-value {
        color: #333;
    }
    .badge-web .badge-value {
        color: #2E7D32;
    }
    .badge-whatsapp .badge-value {
        color: #25D366;
    }
    .badge-email .badge-value {
        color: #D93025;
    }
    .badge-twitter .badge-value {
        color: #1DA1F2;
    }
    </style>
    """, unsafe_allow_html=True)

    # Enlaces como etiquetas con estilo de badge
    st.sidebar.markdown("""
    <div class="badge-container">
        <a href="https://www.linkedin.com/in/alexanderoviedofadul/" target="_blank" class="badge-link badge-linkedin">
            <div class="badge">
                <span class="badge-label">LinkedIn:</span>
                <span class="badge-value">Perfil</span>
            </div>
        </a>
        <a href="https://github.com/bladealex9848" target="_blank" class="badge-link badge-github">
            <div class="badge">
                <span class="badge-label">GitHub:</span>
                <span class="badge-value">bladealex9848</span>
            </div>
        </a>
        <a href="https://twitter.com/bladealex9848" target="_blank" class="badge-link badge-twitter">
            <div class="badge">
                <span class="badge-label">Twitter:</span>
                <span class="badge-value">@bladealex9848</span>
            </div>
        </a>
    </div>
    """, unsafe_allow_html=True)

    # Enlaces de contacto
    st.sidebar.markdown("##### Contacto")
    st.sidebar.markdown("""
    <div class="badge-container">
        <a href="https://alexanderoviedofadul.dev" target="_blank" class="badge-link badge-web">
            <div class="badge">
                <span class="badge-label">Web:</span>
                <span class="badge-value">Portfolio</span>
            </div>
        </a>
        <a href="https://marduk.pro" target="_blank" class="badge-link badge-web">
            <div class="badge">
                <span class="badge-label">Web:</span>
                <span class="badge-value">Marduk.pro</span>
            </div>
        </a>
        <a href="https://wa.me/573015930519" target="_blank" class="badge-link badge-whatsapp">
            <div class="badge">
                <span class="badge-label">WhatsApp:</span>
                <span class="badge-value">Contacto</span>
            </div>
        </a>
        <a href="mailto:alexander.oviedo.fadul@gmail.com" target="_blank" class="badge-link badge-email">
            <div class="badge">
                <span class="badge-label">Email:</span>
                <span class="badge-value">Contacto</span>
            </div>
        </a>
    </div>
    """, unsafe_allow_html=True)

    # Habilidades
    st.sidebar.markdown("##### Habilidades")
    st.sidebar.markdown("""
    - 💻 Desarrollo Web (Python, JavaScript, React)
    - 🤖 Inteligencia Artificial y ML
    - 📊 Análisis de Datos y Visualización
    - 🔄 DevOps y Automatización
    - 🌐 Desarrollo de APIs y Microservicios
    """)

    # Información del proyecto
    st.sidebar.markdown("##### Proyecto")

    # Enlaces del proyecto como etiquetas
    st.sidebar.markdown("""
    <div class="badge-container">
        <a href="https://github.com/bladealex9848/OmniChat" target="_blank" class="badge-link badge-github">
            <div class="badge">
                <span class="badge-label">GitHub:</span>
                <span class="badge-value">Repositorio</span>
            </div>
        </a>
        <a href="https://omnichat.streamlit.app" target="_blank" class="badge-link badge-web">
            <div class="badge">
                <span class="badge-label">Demo:</span>
                <span class="badge-value">Online</span>
            </div>
        </a>
    </div>
    """, unsafe_allow_html=True)

    # Contador de visitantes con estilo mejorado
    st.sidebar.markdown("""
    <div style="margin-top: 10px; text-align: center;">
        <div style="display: inline-block; background-color: #f0f2f6; border-radius: 5px; padding: 5px 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <span style="font-weight: 500; color: #5d5d5d;">Visitantes:</span>
            <img src="https://api.visitorbadge.io/api/visitors?path=https%3A%2F%2Fomnichat.streamlit.app&countColor=%231e7ebf&style=flat&labelStyle=none"
                 style="height: 20px; vertical-align: middle; margin-left: 5px;" alt="Contador de visitantes">
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Tecnologías utilizadas
    st.sidebar.markdown("##### Tecnologías")
    st.sidebar.markdown("""
    <div class="badge-container">
        <div class="badge">
            <span class="badge-label">Python</span>
            <span class="badge-value" style="color: #3572A5;">3.10+</span>
        </div>
        <div class="badge">
            <span class="badge-label">Streamlit</span>
            <span class="badge-value" style="color: #FF4B4B;">1.44.0</span>
        </div>
        <div class="badge">
            <span class="badge-label">LangChain</span>
            <span class="badge-value" style="color: #412991;">0.1.0+</span>
        </div>
        <div class="badge">
            <span class="badge-label">OpenAI</span>
            <span class="badge-value" style="color: #000000;">API</span>
        </div>
        <div class="badge">
            <span class="badge-label">OpenRouter</span>
            <span class="badge-value" style="color: #F9AB00;">API</span>
        </div>
        <div class="badge">
            <span class="badge-label">Mistral</span>
            <span class="badge-value" style="color: #0081CB;">API</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Pie de página
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style="font-size: 0.8em; text-align: center; opacity: 0.7;">
        © 2024 Alexander Oviedo Fadul<br>
        Desarrollado con ❤️ en Colombia
    </div>
    """, unsafe_allow_html=True)

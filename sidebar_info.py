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

    # Estilo CSS para las etiquetas de enlaces e incluir Font Awesome
    st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
    .link-badge {
        display: inline-block;
        padding: 5px 10px;
        margin: 4px 2px;
        border-radius: 5px;
        text-decoration: none;
        font-weight: 500;
        font-size: 0.85em;
        color: white;
        transition: all 0.2s ease;
    }
    .link-badge:hover {
        opacity: 0.85;
        transform: translateY(-2px);
    }
    .linkedin {
        background-color: #0077B5;
    }
    .github {
        background-color: #333;
    }
    .web {
        background-color: #2E7D32;
    }
    .whatsapp {
        background-color: #25D366;
    }
    .email {
        background-color: #D93025;
    }
    .twitter {
        background-color: #1DA1F2;
    }
    </style>
    """, unsafe_allow_html=True)

    # Enlaces como etiquetas con iconos de Font Awesome
    st.sidebar.markdown("""
    <div style="display: flex; flex-wrap: wrap; gap: 8px;">
        <a href="https://www.linkedin.com/in/alexanderoviedofadul/" target="_blank" class="link-badge linkedin">
            <i class="fab fa-linkedin"></i> LinkedIn
        </a>
        <a href="https://github.com/bladealex9848" target="_blank" class="link-badge github">
            <i class="fab fa-github"></i> GitHub
        </a>
        <a href="https://twitter.com/bladealex9848" target="_blank" class="link-badge twitter">
            <i class="fab fa-twitter"></i> Twitter
        </a>
    </div>
    """, unsafe_allow_html=True)

    # Enlaces de contacto
    st.sidebar.markdown("##### Contacto")
    st.sidebar.markdown("""
    <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 10px;">
        <a href="https://alexanderoviedofadul.dev" target="_blank" class="link-badge web">
            <i class="fas fa-globe"></i> Portfolio
        </a>
        <a href="https://marduk.pro" target="_blank" class="link-badge web">
            <i class="fas fa-briefcase"></i> Marduk.pro
        </a>
        <a href="https://wa.me/573015930519" target="_blank" class="link-badge whatsapp">
            <i class="fab fa-whatsapp"></i> WhatsApp
        </a>
        <a href="mailto:alexander.oviedo.fadul@gmail.com" target="_blank" class="link-badge email">
            <i class="fas fa-envelope"></i> Email
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
    <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 10px;">
        <a href="https://github.com/bladealex9848/OmniChat" target="_blank" class="link-badge github">
            <i class="fab fa-github"></i> Repositorio
        </a>
        <a href="https://omnichat.streamlit.app" target="_blank" class="link-badge web">
            <i class="fas fa-globe"></i> Demo Online
        </a>
    </div>
    """, unsafe_allow_html=True)

    # Contador de visitantes
    st.sidebar.markdown("""
    <div style="margin-top: 10px; text-align: center;">
        <img src="https://api.visitorbadge.io/api/visitors?path=https%3A%2F%2Fomnichat.streamlit.app&label=Visitantes&labelColor=%235d5d5d&countColor=%231e7ebf&style=flat" alt="Visitantes">
    </div>
    """, unsafe_allow_html=True)

    # Tecnologías utilizadas
    st.sidebar.markdown("##### Tecnologías")
    st.sidebar.markdown("""
    <div style="display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 10px;">
        <span style="background-color: #3572A5; color: white; padding: 3px 7px; border-radius: 3px; font-size: 0.75em;">Python</span>
        <span style="background-color: #FF4B4B; color: white; padding: 3px 7px; border-radius: 3px; font-size: 0.75em;">Streamlit</span>
        <span style="background-color: #412991; color: white; padding: 3px 7px; border-radius: 3px; font-size: 0.75em;">LangChain</span>
        <span style="background-color: #000000; color: white; padding: 3px 7px; border-radius: 3px; font-size: 0.75em;">OpenAI</span>
        <span style="background-color: #F9AB00; color: white; padding: 3px 7px; border-radius: 3px; font-size: 0.75em;">OpenRouter</span>
        <span style="background-color: #0081CB; color: white; padding: 3px 7px; border-radius: 3px; font-size: 0.75em;">Mistral</span>
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

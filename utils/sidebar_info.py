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
        st.image("assets/profile.jpg", width=60)
    with col2:
        st.markdown("#### Alexander Oviedo Fadul")
        st.markdown(
            """
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                <a href="https://www.linkedin.com/in/alexanderoviedofadul/" target="_blank">
                    <img src="https://img.shields.io/badge/LinkedIn-Perfil-blue?logo=linkedin&style=flat" alt="LinkedIn">
                </a>
                <a href="https://github.com/bladealex9848" target="_blank">
                    <img src="https://img.shields.io/badge/GitHub-Perfil-gray?logo=github&style=flat" alt="GitHub">
                </a>
                <a href="https://marduk.pro" target="_blank">
                    <img src="https://img.shields.io/badge/Web-Marduk.pro-green?logo=web&style=flat" alt="Web">
                </a>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    # Enlaces de contacto
    st.sidebar.markdown("##### Contacto")
    st.sidebar.markdown(
        """
        <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 10px;">
            <a href="https://alexanderoviedofadul.dev" target="_blank">
                <img src="https://img.shields.io/badge/Website-alexanderoviedofadul.dev-green?logo=web&style=flat" alt="Website">
            </a>
            <a href="https://wa.me/573015930519" target="_blank">
                <img src="https://img.shields.io/badge/WhatsApp-Contacto-25D366?logo=whatsapp&style=flat" alt="WhatsApp">
            </a>
            <a href="mailto:alexander.oviedo.fadul@gmail.com" target="_blank">
                <img src="https://img.shields.io/badge/Email-Contacto-red?logo=gmail&style=flat" alt="Email">
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Información del proyecto
    st.sidebar.markdown("##### Proyecto")
    st.sidebar.markdown(
        """
        <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 10px;">
            <a href="https://github.com/bladealex9848/OmniChat" target="_blank">
                <img src="https://img.shields.io/badge/GitHub-Repositorio-gray?logo=github&style=flat" alt="GitHub Repo">
            </a>
            <a href="https://omnichat.streamlit.app" target="_blank">
                <img src="https://img.shields.io/badge/OmniChat-Web-blue?logo=streamlit&style=flat" alt="OmniChat Web">
            </a>
            <img src="https://api.visitorbadge.io/api/visitors?path=https%3A%2F%2Fomnichat.streamlit.app&label=Visitantes&labelColor=%235d5d5d&countColor=%231e7ebf&style=flat" alt="Visitantes">
        </div>
        """,
        unsafe_allow_html=True,
    )

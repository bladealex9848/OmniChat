"""
Utilidades para la configuración y manejo de páginas en Streamlit.
"""

try:
    import streamlit as st
except ImportError:
    # Para pruebas sin streamlit
    class StMock:
        def __init__(self):
            self.session_state = {}
            
        def set_page_config(self, page_title=None, page_icon=None, layout=None, initial_sidebar_state=None):
            pass
            
        def header(self, title):
            print(f"HEADER: {title}")
    
    st = StMock()


def setup_page(title, icon, page_title=None, show_author=True):
    """
    Configura la página de Streamlit de manera consistente.

    Args:
        title (str): Título principal que se mostrará en la página
        icon (str): Icono para la página (emoji)
        page_title (str, optional): Título de la pestaña del navegador. Si es None, se usa el title.
        show_author (bool, optional): Si se debe mostrar la información del autor en la barra lateral.
    """
    if page_title is None:
        page_title = title

    # Configurar la página
    st.set_page_config(
        page_title=page_title,
        page_icon=icon,
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Mostrar el título
    st.header(title)

    # Mostrar información del autor si se solicita
    if show_author:
        try:
            # Intentar importar la función show_author_info
            from sidebar_info import show_author_info
            show_author_info()
        except ImportError:
            try:
                # Intentar importar desde utils.sidebar_info como alternativa
                from utils.sidebar_info import show_author_info
                show_author_info()
            except ImportError:
                # Si no se puede importar, no mostrar la información del autor
                pass

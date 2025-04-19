import os
import json
import time
import logging
import requests
import streamlit as st
from typing import Dict, List, Any, Optional

# Configuración de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("SearchUtils")


class FallbackSearchTool:
    """
    Herramienta de búsqueda con mecanismos de respaldo cuando DuckDuckGo falla.
    Implementa múltiples métodos de búsqueda gratuitos y cambia automáticamente entre ellos.
    """

    def __init__(self, max_retries: int = 2, retry_delay: int = 1):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.last_search_time = 0
        # Solo usar métodos gratuitos que no requieren API keys
        self.search_methods = [
            self._search_with_duckduckgo,
            self._search_with_direct_scraping,
            self._search_with_google_scraping,
            self._search_with_bing_scraping,
        ]

    def run(self, query: str) -> str:
        """
        Ejecuta la búsqueda con mecanismos de respaldo.

        Args:
            query: La consulta de búsqueda

        Returns:
            Resultados de la búsqueda como texto
        """
        # Esperar para evitar rate limits (mínimo 1 segundo entre búsquedas)
        current_time = time.time()
        time_since_last = current_time - self.last_search_time
        if time_since_last < 1:
            time.sleep(1 - time_since_last)

        self.last_search_time = time.time()

        # Intentar cada método de búsqueda
        errors = []
        for search_method in self.search_methods:
            for attempt in range(self.max_retries):
                try:
                    results = search_method(query)
                    if results:
                        return results
                except Exception as e:
                    error_msg = f"Error con {search_method.__name__}: {str(e)}"
                    logger.warning(error_msg)
                    errors.append(error_msg)
                    time.sleep(self.retry_delay)

        # Si todos los métodos fallan, devolver un mensaje de error con detalles
        error_details = "\n".join(errors)
        return f"No se pudieron obtener resultados de búsqueda para '{query}'. Errores encontrados:\n{error_details}"

    def _search_with_duckduckgo(self, query: str) -> str:
        """
        Búsqueda usando DuckDuckGo directamente con requests para evitar problemas de la biblioteca.
        """
        try:
            from duckduckgo_search import DDGS

            # Crear una nueva sesión para cada búsqueda
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))

            if not results:
                return ""

            formatted_results = []
            for result in results:
                title = result.get("title", "Sin título")
                body = result.get("body", "Sin contenido")
                href = result.get("href", "Sin enlace")
                formatted_results.append(f"### {title}\n{body}\nFuente: {href}\n")

            return "\n".join(formatted_results)
        except Exception as e:
            logger.error(f"Error en búsqueda DuckDuckGo: {str(e)}")
            raise

    def _search_with_serper(self, query: str) -> str:
        """
        Búsqueda usando Serper.dev API (requiere API key).
        """
        api_key = None
        if hasattr(st, "secrets") and "SERPER_API_KEY" in st.secrets:
            api_key = st.secrets["SERPER_API_KEY"]
        elif os.environ.get("SERPER_API_KEY"):
            api_key = os.environ.get("SERPER_API_KEY")

        if not api_key:
            raise ValueError("No se encontró API key para Serper.dev")

        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": query, "gl": "es", "hl": "es"})
        headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}

        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        search_results = response.json()

        if not search_results.get("organic"):
            return ""

        formatted_results = []
        for result in search_results.get("organic", [])[:5]:
            title = result.get("title", "Sin título")
            snippet = result.get("snippet", "Sin descripción")
            link = result.get("link", "Sin enlace")
            formatted_results.append(f"### {title}\n{snippet}\nFuente: {link}\n")

        return "\n".join(formatted_results)

    def _search_with_serpapi(self, query: str) -> str:
        """
        Búsqueda usando SerpAPI (requiere API key).
        """
        api_key = None
        if hasattr(st, "secrets") and "SERPAPI_API_KEY" in st.secrets:
            api_key = st.secrets["SERPAPI_API_KEY"]
        elif os.environ.get("SERPAPI_API_KEY"):
            api_key = os.environ.get("SERPAPI_API_KEY")

        if not api_key:
            raise ValueError("No se encontró API key para SerpAPI")

        params = {
            "engine": "google",
            "q": query,
            "api_key": api_key,
            "hl": "es",
            "gl": "es",
        }

        response = requests.get("https://serpapi.com/search", params=params)
        response.raise_for_status()
        search_results = response.json()

        if not search_results.get("organic_results"):
            return ""

        formatted_results = []
        for result in search_results.get("organic_results", [])[:5]:
            title = result.get("title", "Sin título")
            snippet = result.get("snippet", "Sin descripción")
            link = result.get("link", "Sin enlace")
            formatted_results.append(f"### {title}\n{snippet}\nFuente: {link}\n")

        return "\n".join(formatted_results)

    def _search_with_direct_scraping(self, query: str) -> str:
        """
        Búsqueda mediante scraping directo (método de último recurso).
        """
        try:
            # Usar una URL de búsqueda alternativa que sea menos propensa a bloqueos
            search_url = (
                f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
            )

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }

            response = requests.get(search_url, headers=headers)
            response.raise_for_status()

            # Usar BeautifulSoup para extraer resultados
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(response.text, "html.parser")

            results = []
            for result in soup.select(".result")[:5]:  # Limitar a 5 resultados
                title_elem = result.select_one(".result__title")
                snippet_elem = result.select_one(".result__snippet")
                url_elem = result.select_one(".result__url")

                title = title_elem.get_text() if title_elem else "Sin título"
                snippet = snippet_elem.get_text() if snippet_elem else "Sin descripción"
                url = url_elem.get_text() if url_elem else "Sin URL"

                results.append(f"### {title}\n{snippet}\nFuente: {url}\n")

            if not results:
                return ""

            return "\n".join(results)
        except Exception as e:
            logger.error(f"Error en scraping directo: {str(e)}")
            raise


# Función para obtener una instancia de la herramienta de búsqueda
def get_search_tool():
    """
    Obtiene una instancia de la herramienta de búsqueda con respaldo.

    Returns:
        FallbackSearchTool: Herramienta de búsqueda con mecanismos de respaldo
    """
    return FallbackSearchTool()

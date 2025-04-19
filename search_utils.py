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

    def _search_with_google_scraping(self, query: str) -> str:
        """
        Búsqueda mediante scraping directo de Google (método gratuito).
        """
        try:
            # Codificar la consulta para la URL
            encoded_query = requests.utils.quote(query)

            # Construir URL de búsqueda de Google
            search_url = f"https://www.google.com/search?q={encoded_query}&hl=es"

            # Usar un User-Agent de navegador para evitar bloqueos
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
                "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
                "Referer": "https://www.google.com/",
            }

            # Realizar la solicitud con un timeout para evitar bloqueos
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()

            # Usar BeautifulSoup para extraer resultados
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(response.text, "html.parser")

            # Extraer resultados de búsqueda
            results = []
            for result in soup.select("div.g")[:5]:  # Limitar a 5 resultados
                # Extraer título
                title_elem = result.select_one("h3")
                title = title_elem.get_text() if title_elem else "Sin título"

                # Extraer snippet/descripción
                snippet_elem = result.select_one("div.VwiC3b")
                snippet = snippet_elem.get_text() if snippet_elem else "Sin descripción"

                # Extraer enlace
                link_elem = result.select_one("a")
                link = link_elem.get("href") if link_elem else "Sin enlace"
                if link.startswith("/url?q="):
                    link = link.split("/url?q=")[1].split("&")[0]

                results.append(f"### {title}\n{snippet}\nFuente: {link}\n")

            if not results:
                return ""

            return "\n".join(results)
        except Exception as e:
            logger.error(f"Error en scraping de Google: {str(e)}")
            raise

    def _search_with_bing_scraping(self, query: str) -> str:
        """
        Búsqueda mediante scraping directo de Bing (método gratuito).
        """
        try:
            # Codificar la consulta para la URL
            encoded_query = requests.utils.quote(query)

            # Construir URL de búsqueda de Bing
            search_url = f"https://www.bing.com/search?q={encoded_query}&setlang=es"

            # Usar un User-Agent de navegador para evitar bloqueos
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
                "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
                "Referer": "https://www.bing.com/",
            }

            # Realizar la solicitud con un timeout para evitar bloqueos
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()

            # Usar BeautifulSoup para extraer resultados
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(response.text, "html.parser")

            # Extraer resultados de búsqueda
            results = []
            for result in soup.select(".b_algo")[:5]:  # Limitar a 5 resultados
                # Extraer título
                title_elem = result.select_one("h2")
                title = title_elem.get_text() if title_elem else "Sin título"

                # Extraer snippet/descripción
                snippet_elem = result.select_one(".b_caption p")
                snippet = snippet_elem.get_text() if snippet_elem else "Sin descripción"

                # Extraer enlace
                link_elem = result.select_one("h2 a")
                link = link_elem.get("href") if link_elem else "Sin enlace"

                results.append(f"### {title}\n{snippet}\nFuente: {link}\n")

            if not results:
                return ""

            return "\n".join(results)
        except Exception as e:
            logger.error(f"Error en scraping de Bing: {str(e)}")
            raise

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

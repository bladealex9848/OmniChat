import os
import requests
import logging
import json
import time
import random
from typing import List, Dict, Any, Optional, Union
import streamlit as st

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def get_google_search_results(query: str) -> Optional[List[Dict[str, str]]]:
    """
    Realiza una búsqueda utilizando la API de Google Programmable Search Engine.

    Args:
        query: La consulta de búsqueda

    Returns:
        Lista de resultados o None si hay un error
    """
    try:
        # Obtener credenciales
        api_key = st.secrets.get("GOOGLE_PSE_API_KEY")
        engine_id = st.secrets.get("GOOGLE_PSE_ENGINE_ID")

        if not api_key or not engine_id:
            logger.warning("Faltan credenciales para Google Search API")
            return None

        # Construir URL
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": api_key,
            "cx": engine_id,
            "q": query,
            "num": 5  # Número de resultados
        }

        # Realizar solicitud
        response = requests.get(url, params=params)
        response.raise_for_status()

        # Procesar resultados
        data = response.json()
        if "items" not in data:
            logger.warning("No se encontraron resultados en Google Search")
            return []

        results = []
        for item in data["items"]:
            results.append({
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", "")
            })

        return results

    except Exception as e:
        logger.error(f"Error en Google Search: {str(e)}")
        return None

def get_exa_search_results(query: str) -> Optional[List[Dict[str, str]]]:
    """
    Realiza una búsqueda utilizando la API de Exa.

    Args:
        query: La consulta de búsqueda

    Returns:
        Lista de resultados o None si hay un error
    """
    try:
        # Obtener credenciales
        api_key = st.secrets.get("EXA_API_KEY")

        if not api_key:
            logger.warning("Falta API key para Exa")
            return None

        # Construir solicitud
        url = "https://api.exa.ai/search"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key
        }
        data = {
            "query": query,
            "contents": {
                "text": {"maxCharacters": 1000}
            }
        }

        # Realizar solicitud
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        # Procesar resultados
        results_data = response.json()
        if "results" not in results_data:
            logger.warning("No se encontraron resultados en Exa")
            return []

        results = []
        for item in results_data["results"]:
            results.append({
                "title": item.get("title", ""),
                "link": item.get("url", ""),
                "snippet": item.get("text", "")
            })

        return results

    except Exception as e:
        logger.error(f"Error en Exa Search: {str(e)}")
        return None

# Eliminados los métodos que no funcionan: get_you_search_results y get_tavily_search_results

def get_duckduckgo_search_results(query: str, max_retries: int = 3) -> Optional[List[Dict[str, str]]]:
    """
    Realiza una búsqueda utilizando DuckDuckGo.

    Args:
        query: La consulta de búsqueda
        max_retries: Número máximo de intentos

    Returns:
        Lista de resultados o None si hay un error
    """
    try:
        from duckduckgo_search import DDGS

        for attempt in range(max_retries):
            try:
                with DDGS() as ddgs:
                    results_raw = list(ddgs.text(query, max_results=5))

                if not results_raw:
                    logger.warning("No se encontraron resultados en DuckDuckGo")
                    return []

                results = []
                for item in results_raw:
                    results.append({
                        "title": item.get("title", ""),
                        "link": item.get("href", ""),
                        "snippet": item.get("body", "")
                    })

                return results

            except Exception as e:
                if "Ratelimit" in str(e) and attempt < max_retries - 1:
                    wait_time = (2**attempt) + random.uniform(0, 1)
                    time.sleep(wait_time)
                else:
                    raise

    except Exception as e:
        logger.error(f"Error en DuckDuckGo Search: {str(e)}")
        return None

# Lista de User-Agents para evitar bloqueos
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
]

def get_random_user_agent():
    """Devuelve un User-Agent aleatorio para evitar bloqueos"""
    return random.choice(USER_AGENTS)

# 6. GOOGLE SCRAPING (PRIMER RESPALDO)
# Eliminados los métodos que no funcionan: get_google_scraping_results y get_bing_scraping_results

# 8. DUCKDUCKGO HTML SCRAPING (RESPALDO FINAL)
def get_duckduckgo_html_results(query: str) -> Optional[List[Dict[str, str]]]:
    """
    Realiza una búsqueda mediante scraping HTML de DuckDuckGo.

    Args:
        query: La consulta de búsqueda

    Returns:
        Lista de resultados o None si hay un error
    """
    try:
        # Importar BeautifulSoup
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            logger.error("No se pudo importar bs4. Instálalo con 'pip install beautifulsoup4'")
            return None

        # Construir la URL de búsqueda de DuckDuckGo
        search_url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"

        # Realizar la solicitud con un User-Agent aleatorio
        headers = {"User-Agent": get_random_user_agent()}

        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()

        # Parsear el HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extraer resultados
        results = []
        search_results = soup.select('div.result')

        for result in search_results[:5]:  # Limitar a 5 resultados
            title_element = result.select_one('a.result__a')
            link_element = result.select_one('a.result__a')
            snippet_element = result.select_one('a.result__snippet')

            if title_element and link_element and snippet_element:
                title = title_element.get_text()
                link = link_element.get('href')
                snippet = snippet_element.get_text()

                results.append({
                    "title": title,
                    "link": link,
                    "snippet": snippet
                })

        if not results:
            logger.warning("No se encontraron resultados en DuckDuckGo HTML Scraping")
            return []

        logger.info(f"Búsqueda exitosa con DuckDuckGo HTML Scraping: {len(results)} resultados")
        return results

    except Exception as e:
        logger.error(f"Error en DuckDuckGo HTML Scraping: {str(e)}")
        return None

def perform_web_search(query: str) -> List[Dict[str, str]]:
    """
    Realiza una búsqueda web utilizando múltiples servicios en orden de prioridad.

    Orden de prioridad (métodos que funcionan correctamente):
    1. DuckDuckGo (API) - Método gratuito principal
    2. DuckDuckGo HTML (Scraping) - Método gratuito de respaldo
    3. Google PSE (API) - API de respaldo 1
    4. Exa (API) - API de respaldo 2

    Args:
        query: La consulta de búsqueda

    Returns:
        Lista de resultados de búsqueda
    """
    # Orden de prioridad: primero métodos gratuitos, luego APIs como respaldo

    # Métodos gratuitos (primero)
    free_search_methods = [
        ("DuckDuckGo Search", get_duckduckgo_search_results),
        ("DuckDuckGo HTML", get_duckduckgo_html_results)
    ]

    # Probar primero los métodos gratuitos
    for service_name, search_method in free_search_methods:
        logger.info(f"Intentando búsqueda con {service_name}")
        results = search_method(query)

        if results:
            logger.info(f"Búsqueda exitosa con {service_name}")
            # Añadir el nombre del servicio a cada resultado
            for result in results:
                result["service"] = service_name
            return results

    # Si los métodos gratuitos fallan, usar las APIs como respaldo
    logger.info("Los métodos gratuitos fallaron. Usando APIs como respaldo.")

    # APIs como respaldo (solo las que funcionan)
    api_search_methods = [
        ("Google Search", get_google_search_results),
        ("Exa Search", get_exa_search_results)
    ]

    # Probar las APIs como respaldo
    for service_name, search_method in api_search_methods:
        logger.info(f"Intentando búsqueda con {service_name}")
        results = search_method(query)

        if results:
            logger.info(f"Búsqueda exitosa con {service_name}")
            # Añadir el nombre del servicio a cada resultado
            for result in results:
                result["service"] = service_name
            return results

    # Si todo falla, devolver una lista vacía
    logger.warning("Todas las búsquedas fallaron")
    return []

def format_search_results(results: List[Dict[str, str]]) -> str:
    """
    Formatea los resultados de búsqueda en un texto legible.

    Args:
        results: Lista de resultados de búsqueda

    Returns:
        Texto formateado con los resultados
    """
    if not results:
        return "No se encontraron resultados."

    formatted_text = ""
    for i, result in enumerate(results, 1):
        formatted_text += f"### {i}. {result['title']}\n"
        formatted_text += f"{result['snippet']}\n"
        formatted_text += f"**Fuente:** [{result['link']}]({result['link']})\n\n"

    return formatted_text

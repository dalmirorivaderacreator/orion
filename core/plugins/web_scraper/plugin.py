"""
Web Scraper Plugin

Provides web scraping and content extraction capabilities.
"""

import os
from urllib.parse import urljoin, urlparse
from core.plugins.plugin_base import PluginBase
from registry import register_function


class WebScraperPlugin(PluginBase):
    """
    Plugin for web scraping operations.

    Provides:
    - Web page content extraction using CSS selectors
    - Link extraction from web pages
    - Image downloading from web pages

    Note: Requires beautifulsoup4 and lxml packages.
    """

    @property
    def name(self) -> str:
        return "web_scraper"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Web scraping: extract content, links, and download images"

    @property
    def author(self) -> str:
        return "ORION Team"

    @property
    def dependencies(self) -> list:
        return ["beautifulsoup4", "lxml"]

    def initialize(self) -> bool:
        """Initialize the web scraper plugin."""
        # Check if required packages are available
        try:
            import bs4  # pylint: disable=import-outside-toplevel,unused-import
            import lxml  # pylint: disable=import-outside-toplevel,unused-import
            return True
        except ImportError as e:
            self.error_state = f"Missing dependency: {e}"
            return False

    def shutdown(self) -> None:
        """Clean up resources."""

    def register_functions(self) -> None:  # pylint: disable=too-many-statements
        """Register web scraping functions with ORION."""

        @register_function(
            name="scrape_webpage",
            description="Extrae contenido de una página web usando selectores CSS",
            argument_types={
                "url": "str",
                "selector": "str"
            }
        )
        def scrape_webpage(url: str, selector: str) -> str:
            """
            Extract content from a webpage using CSS selectors.

            Args:
                url: URL of the webpage to scrape
                selector: CSS selector to extract content

            Returns:
                Extracted content or error message
            """
            try:
                # pylint: disable=import-outside-toplevel
                import requests
                from bs4 import BeautifulSoup

                response = requests.get(url, timeout=30)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'lxml')
                elements = soup.select(selector)

                if not elements:
                    return f"No se encontraron elementos con el selector '{selector}'"

                results = []
                for i, element in enumerate(elements[:10], 1):  # Limit to 10 results
                    text = element.get_text(strip=True)
                    results.append(f"{i}. {text}")

                return (
                    f"Extraídos {len(elements)} elementos de {url}:\n" +
                    "\n".join(results)
                )

            except Exception as e:  # pylint: disable=broad-except
                return f"Error al extraer contenido: {str(e)}"

        @register_function(
            name="extract_links",
            description="Extrae todos los enlaces de una página web",
            argument_types={"url": "str"}
        )
        def extract_links(url: str) -> str:
            """
            Extract all links from a webpage.

            Args:
                url: URL of the webpage

            Returns:
                List of links found
            """
            try:
                # pylint: disable=import-outside-toplevel
                import requests
                from bs4 import BeautifulSoup

                response = requests.get(url, timeout=30)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'lxml')
                links = []

                for link in soup.find_all('a', href=True):
                    href = link['href']
                    # Convert relative URLs to absolute
                    absolute_url = urljoin(url, href)
                    links.append(absolute_url)

                # Remove duplicates and limit
                unique_links = list(dict.fromkeys(links))[:50]

                result = f"Encontrados {len(links)} enlaces en {url}:\n"
                for i, link in enumerate(unique_links, 1):
                    result += f"{i}. {link}\n"

                if len(links) > 50:
                    result += f"\n(Mostrando primeros 50 de {len(links)} enlaces)"

                return result

            except Exception as e:  # pylint: disable=broad-except
                return f"Error al extraer enlaces: {str(e)}"

        @register_function(
            name="download_images",
            description="Descarga todas las imágenes de una página web",
            argument_types={
                "url": "str",
                "output_dir": "str"
            }
        )
        def download_images(url: str, output_dir: str) -> str:  # pylint: disable=too-many-locals
            """
            Download all images from a webpage.

            Args:
                url: URL of the webpage
                output_dir: Directory to save downloaded images

            Returns:
                Status message with download count
            """
            try:
                # pylint: disable=import-outside-toplevel
                import requests
                from bs4 import BeautifulSoup

                # Create output directory
                os.makedirs(output_dir, exist_ok=True)

                response = requests.get(url, timeout=30)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'lxml')
                images = soup.find_all('img', src=True)

                downloaded = 0
                for i, img in enumerate(images, 1):
                    img_url = urljoin(url, img['src'])

                    try:
                        img_response = requests.get(img_url, timeout=30)
                        img_response.raise_for_status()

                        # Generate filename from URL
                        parsed = urlparse(img_url)
                        filename = os.path.basename(parsed.path) or f"image_{i}.jpg"
                        filepath = os.path.join(output_dir, filename)

                        with open(filepath, 'wb') as f:
                            f.write(img_response.content)

                        downloaded += 1

                    except Exception:  # pylint: disable=broad-except
                        continue

                return (
                    f"Descargadas {downloaded}/{len(images)} imágenes de {url}\n"
                    f"Guardadas en: {output_dir}"
                )

            except Exception as e:  # pylint: disable=broad-except
                return f"Error al descargar imágenes: {str(e)}"

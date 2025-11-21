"""
Operaciones de archivos para ORION (Crear carpetas, listar, descargar).
"""
import os
import requests
from registry import register_function

@register_function(
    name="create_folder",
    description="Crea una carpeta nueva",
    argument_types={"path": "str"}
)
def create_folder(path):
    """Crea un directorio si no existe."""
    os.makedirs(path, exist_ok=True)
    return f"Carpeta creada: {path}"

@register_function(
    name="list_files",
    description="Lista archivos en una carpeta",
    argument_types={"path": "str"}
)
def list_files(path):
    """Lista los archivos en el directorio especificado."""
    files = os.listdir(path)
    return f"Archivos en {path}: {', '.join(files)}"

@register_function(
    name="download_file",
    description="Descarga un archivo de internet a tu computadora",
    argument_types={"url": "str", "output_path": "str"}
)
def download_file(url, output_path):
    """Descarga un archivo desde una URL."""
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'wb') as f:
        f.write(response.content)

    return f"Archivo descargado: {output_path} ({(len(response.content))} bytes)"

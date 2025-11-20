import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from registry import register_function

@register_function(
    name="create_folder",
    description="Crea una carpeta nueva",
    argument_types={"path": "str"}
)
def create_folder(path):
    os.makedirs(path, exist_ok=True)
    return f"Carpeta creada: {path}"

@register_function(
    name="list_files", 
    description="Lista archivos en una carpeta",
    argument_types={"path": "str"}
)
def list_files(path):
    files = os.listdir(path)
    return f"Archivos en {path}: {', '.join(files)}"
@register_function(
    name="download_file",
    description="Descarga un archivo de internet a tu computadora",
    argument_types={"url": "str", "output_path": "str"}
)
def download_file(url, output_path):
    import requests
    response = requests.get(url)
    response.raise_for_status()
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'wb') as f:
        f.write(response.content)
    
    return f"Archivo descargado: {output_path} ({(len(response.content))} bytes)"
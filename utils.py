"""
Utilidades generales para ORION.
"""

def normalize_path(path: str) -> str:
    """
    Normaliza rutas de archivo para evitar problemas con separadores y prefijos.
    Ej: ".//data//file.txt" -> "data/file.txt"
    """
    if not path:
        return path

    # Reemplazar backslashes con forward slashes
    clean_path = path.replace("\\", "/")

    # Eliminar dobles slashes primero para simplificar
    while "//" in clean_path:
        clean_path = clean_path.replace("//", "/")

    # Eliminar prefijos comunes que confunden
    if clean_path.startswith("./"):
        clean_path = clean_path[2:]
    elif clean_path.startswith("/"):
        clean_path = clean_path[1:]


    # Eliminar espacios en blanco
    clean_path = clean_path.strip()

    return clean_path

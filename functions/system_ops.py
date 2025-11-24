"""
Operaciones del sistema para ORION (Capacidades, info).
"""
from registry import register_function, get_available_functions


@register_function(
    name="get_capabilities",
    description="Devuelve una lista de lo que ORION puede hacer",
    argument_types={}
)
def get_capabilities():
    """Devuelve un resumen de las funciones disponibles."""
    functions = get_available_functions()
    capabilities = ["🚀 **Funciones Disponibles en ORION:**"]

    for name, info in functions.items():
        capabilities.append(f"- `{name}`: {info['description']}")

    return "\n".join(capabilities)


@register_function(
    name="set_preference",
    description="Guarda una preferencia del usuario (ej: carpeta favorita, tema)",
    argument_types={
        "key": "str",
         "value": "str"})
def set_preference(key: str, value: str) -> str:
    """Guarda una preferencia en la base de datos."""
    # pylint: disable=import-outside-toplevel
    import database
    database.set_preference(key, value)
    return f"✅ Preferencia guardada: {key} = {value}"


@register_function(
    name="get_preference",
    description="Obtiene el valor de una preferencia guardada (ej: fav_color)",
    argument_types={"key": "str"}
)
def get_preference(key: str) -> str:
    """Obtiene una preferencia de la base de datos."""
    # pylint: disable=import-outside-toplevel
    import database
    value = database.get_preference(key)
    if value:
        return f"✅ Preferencia '{key}': {value}"
    return f"ℹ️ No se encontró preferencia para '{key}'"

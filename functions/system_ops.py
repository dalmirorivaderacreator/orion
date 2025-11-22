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

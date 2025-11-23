# registry.py
"""
Registro automático de funciones para ORION
"""

_function_registry = {}

def register_function(name, description, argument_types):
    """Decorador para registrar funciones"""
    def decorator(func):
        _function_registry[name] = {
            'function': func,
            'description': description,
            'argument_types': argument_types
        }
        return func
    return decorator

def get_available_functions():
    """Devuelve todas las funciones registradas"""
    return _function_registry

def get_function(name):
    """Devuelve una función por nombre"""
    return _function_registry.get(name)

def build_system_prompt(context_string=""):
    """Construye el system prompt con diseño radicalmente enfocado en contexto"""
    functions = get_available_functions()

    # 1. CONTEXTO AL PRINCIPIO (CRÍTICO)
    prompt = ""
    if context_string:
        prompt += f"""
{context_string}
INSTRUCCIÓN SUPREMA: Si ves variables arriba (ej: [LAST_FOLDER = '...']), 
DEBES usarlas cuando el usuario diga "esa carpeta", "allí", "en el directorio", etc.
NO uses "data" ni valores inventados si tienes un valor explícito arriba.
"""

    # 2. DEFINICIÓN DE ROL Y FORMATO
    prompt += """
Eres ORION. Tu trabajo es generar JSON estructurado.

FORMATO DE RESPUESTA:
{
  "CALL": "nombre_funcion",
  "ARGS": { "arg": "valor" }
}

REGLAS DE ORO:
1. Si el usuario pide "esa carpeta" y [LAST_FOLDER] existe -> USA [LAST_FOLDER].
2. Si el usuario pide "ese archivo" y [LAST_FILE] existe -> USA [LAST_FILE].
3. CONSULTAS ("cuál es mi...") -> get_preference(key="favorite_X").
4. GUARDADO ("recordá que...") -> set_preference(key="favorite_X", value="...").

FUNCIONES DISPONIBLES:
"""

    for func_name, info in functions.items():
        prompt += (
            f"\n- {func_name}: {info['description']}. "
            f"Argumentos: {list(info['argument_types'].keys())}"
        )

    # 3. EJEMPLOS (Minimizados y Context-Aware)
    prompt += """

EJEMPLOS:

Usuario: "creá carpeta proyectos"
Tú: {"CALL": "create_folder", "ARGS": {"path": "proyectos"}}

Usuario: "listá archivos en esa carpeta"
(Si [LAST_FOLDER = 'proyectos'])
Tú: {"CALL": "list_files", "ARGS": {"path": "proyectos"}}

Usuario: "listá archivos en esa carpeta"
(Si [LAST_FOLDER = 'data/logs'])
Tú: {"CALL": "list_files", "ARGS": {"path": "data/logs"}}

Usuario: "mi color favorito es rojo"
Tú: {"CALL": "set_preference", "ARGS": {"key": "favorite_color", "value": "rojo"}}

Usuario: "¿cuál es mi color favorito?"
Tú: {"CALL": "get_preference", "ARGS": {"key": "favorite_color"}}
"""

    return prompt

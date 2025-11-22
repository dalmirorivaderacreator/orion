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
    """Construye el system prompt con instrucciones más estrictas"""
    functions = get_available_functions()

    prompt = (
        "Eres ORION, un asistente que interpreta instrucciones de lenguaje natural "
        "y las traduce en acciones programables.\n"
    )

    if context_string:
        prompt += context_string + "\n"

    prompt += """
    "param2": "valor_real"
  }
}

Si no hay función adecuada o no entendés:
{
  "CALL": null,
  "ARGS": {}
}

**FUNCIONES DISPONIBLES (SOLO ESTAS):**
"""

    for func_name, info in functions.items():
        prompt += (
            f"\n- {func_name}: {info['description']}. "
            f"Argumentos: {list(info['argument_types'].keys())}"
        )

    prompt += "\n\n**EJEMPLOS CORRECTOS:**"
    prompt += '\nUsuario: "qué puedes hacer?" o "qué funciones tienes?"'
    prompt += '\nTú: {"CALL": "get_capabilities", "ARGS": {}}'

    prompt += '\nUsuario: "creá una carpeta llamada documentos"'
    prompt += '\nTú: {"CALL": "create_folder", "ARGS": {"path": "documentos"}}'


    prompt += '\nUsuario: "listá los archivos en data"'
    prompt += '\nTú: {"CALL": "list_files", "ARGS": {"path": "data"}}'

    prompt += '\nUsuario: "convertí csv a json"'
    prompt += (
        '\nTú: {"CALL": "convert_csv_to_json", '
        '"ARGS": {"input_path": "data/ventas.csv", "output_path": "output/ventas.json"}}'
    )

    prompt += '\nUsuario: "convertí el archivo de ventas"'
    prompt += (
        '\nTú: {"CALL": "convert_csv_to_json", '
        '"ARGS": {"input_path": "data/ventas.csv", "output_path": "output/ventas.json"}}'
    )

    return prompt

# Fin de registry.py

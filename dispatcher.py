from registry import get_function

def dispatch(function_name: str, arguments: dict):
    """
    Ejecuta funciones registradas con manejo elegante de errores
    """
    # Normalizar nombres de argumentos del DSL
    if "input" in arguments:
        arguments["input_path"] = arguments.pop("input")
    if "output" in arguments:
        arguments["output_path"] = arguments.pop("output")

    try:
        # Buscar la función en el registro
        function_info = get_function(function_name)
        
        if not function_info:
            available = list(get_function("__dummy__") or [])
            return f"❌ Función '{function_name}' no encontrada. Funciones disponibles: {', '.join(available)}"
        
        # Validar argumentos requeridos
        required_args = function_info['argument_types'].keys()
        missing_args = [arg for arg in required_args if arg not in arguments]
        
        if missing_args:
            return f"❌ Faltan argumentos para '{function_name}': {missing_args}. Argumentos requeridos: {list(required_args)}"
        
        # Ejecutar la función real
        result = function_info['function'](**arguments)
        return f"✅ {result}"
        
    except FileNotFoundError as e:
        return f"❌ Archivo no encontrado: {str(e)}"
    except PermissionError as e:
        return f"❌ Error de permisos: {str(e)}"
    except KeyError as e:
        return f"❌ Columna no encontrada en los datos: {str(e)}"
    except Exception as e:
        return f"❌ Error ejecutando '{function_name}': {str(e)}"
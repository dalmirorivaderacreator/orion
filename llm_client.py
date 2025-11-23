import json
import os
import requests
from registry import build_system_prompt
from logger import logger

def _validate_and_clean_json(response_text):
    """Valida y limpia el JSON del LLM, forzando el formato correcto"""
    try:
        # Limpiar el texto
        text = response_text.strip()

        # Remover code blocks
        if text.startswith('```json'):
            text = text[7:-3].strip()
        elif text.startswith('```'):
            text = text[3:-3].strip()

        # Parsear JSON
        data = json.loads(text)

        # Validar estructura básica
        if not isinstance(data, dict):
            logger.warning("JSON parseado no es dict", extra={"extra_data": {"parsed": data}})
            return {"CALL": None, "ARGS": {}}

        # Forzar formato ORION
        if "CALL" not in data:
            logger.warning("JSON falta key CALL", extra={"extra_data": {"keys": list(data.keys())}})
            return {"CALL": None, "ARGS": {}}

        # Asegurar que ARGS es un dict
        if "ARGS" not in data or not isinstance(data["ARGS"], dict):
            data["ARGS"] = {}

        return data

    except (json.JSONDecodeError, KeyError, TypeError) as e:
        logger.error(
            "Error validando JSON: %s", e,
            extra={"extra_data": {"raw_text": response_text}}
        )
        return {"CALL": None, "ARGS": {}}

def ask_orion(user_prompt, context_manager=None):
    """
    Intenta con Ollama, si falla usa fallback inteligente
    """

    try:
        logger.debug("Enviando request a Ollama...")
        # Obtener contexto si existe
        context_str = context_manager.get_context_string() if context_manager else ""

        # PRE-PROCESAMIENTO TÉCNICO
        final_prompt = _preprocess_prompt(user_prompt, context_manager)

        # Intento con Ollama real
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                "model": "phi3:mini",
                "prompt": final_prompt,
                "system": build_system_prompt(context_str),
                "stream": False,
                "format": "json"  # <-- FORZAR JSON
            },
            timeout=30
        )


        if response.status_code == 200:
            result = response.json()
            response_text = result['response'].strip()

            logger.debug(
                "Respuesta raw Ollama recibida",
                extra={"extra_data": {"response_length": len(response_text)}}
            )

            # Limpiar posibles code blocks
            if response_text.startswith('```json'):
                response_text = response_text[7:-3].strip()
            elif response_text.startswith('```'):
                response_text = response_text[3:-3].strip()

            parsed = _validate_and_clean_json(response_text)
            print(f"🔍 LLM respondió (validado): {parsed}")
            logger.info("LLM interpretó comando", extra={"extra_data": {"parsed": parsed}})
            return parsed

        logger.error("Ollama error HTTP %s", response.status_code)
        raise RuntimeError(f"HTTP {response.status_code}")

    except Exception as e:
        print(f"⚠️  Ollama no disponible ({e}), usando fallback inteligente...")
        logger.warning("Fallo Ollama (%s), activando Smart Fallback", e)
        return _smart_fallback(user_prompt, context_manager)

def _preprocess_prompt(user_prompt, context_manager):
    """
    Reemplaza referencias contextuales ("esa carpeta", "ahí") 
    con los valores reales ANTES de enviar al LLM.
    """
    if not context_manager:
        return user_prompt
    
    import re
    processed_prompt = user_prompt
    ctx = context_manager.context
    
    # 1. Reemplazar referencias a CARPETA
    if ctx.get("last_folder"):
        folder = ctx["last_folder"]
        # Variaciones comunes
        patterns = [
            r"\besa carpeta\b", 
            r"\bese directorio\b", 
            r"\bahí\b", 
            r"\ballí\b",
            r"\ben la carpeta\b"
        ]
        for pattern in patterns:
            processed_prompt = re.sub(pattern, folder, processed_prompt, flags=re.IGNORECASE)

    # 2. Reemplazar referencias a ARCHIVO
    if ctx.get("last_file"):
        file_path = ctx["last_file"]
        patterns = [
            r"\bese archivo\b", 
            r"\bese documento\b",
            r"\bel archivo generado\b"
        ]
        for pattern in patterns:
            processed_prompt = re.sub(pattern, file_path, processed_prompt, flags=re.IGNORECASE)
            
    if processed_prompt != user_prompt:
        logger.info("Prompt pre-procesado: '%s' -> '%s'", user_prompt, processed_prompt)
        print(f"Contexto aplicado: '{user_prompt}' -> '{processed_prompt}'")

        
    return processed_prompt

def _smart_fallback(user_prompt, context_manager=None):
    """Fallback más inteligente que entiende contexto"""
    # ... (resto de la función igual)

    prompt_lower = user_prompt.lower()

    # CREAR CARPETA
    if any(word in prompt_lower for word in ['carpeta', 'folder', 'directorio', 'mkdir']):
        folder_name = "carpeta_nueva"
        words = user_prompt.split()
        for i, word in enumerate(words):
            if word in ['carpeta', 'folder', 'directorio'] and i + 1 < len(words):
                folder_name = words[i + 1]
                break
        return {"CALL": "create_folder", "ARGS": {"path": folder_name}}

    # LISTAR ARCHIVOS
    if any(word in prompt_lower for word in ['lista', 'archivos', 'files', 'ls', 'dir']):
        path = "."
        # Intentar usar contexto primero
        if context_manager and context_manager.context.get("last_folder"):
            path = context_manager.context["last_folder"]

        # Overrides específicos
        if 'data' in prompt_lower:
            path = "data"
        elif 'output' in prompt_lower:
            path = "output"

        return {"CALL": "list_files", "ARGS": {"path": path}}

    # CONVERTIR CSV - SIEMPRE usar archivo conocido
    if any(word in prompt_lower for word in ['convert', 'csv', 'json']):
        return {
            "CALL": "convert_csv_to_json",
            "ARGS": {
                "input_path": "data/ventas.csv",  # ARCHIVO FIJO QUE EXISTE
                "output_path": "output/ventas.json"
            }
        }

    # ANALIZAR DATOS - NUEVO CASO
    if any(word in prompt_lower for word in ['analiz', 'analyze', 'estadistic', 'metric']):
        input_file = "data/ventas.csv"  # default
        if 'iris' in prompt_lower:
            input_file = "data/iris.csv"

        return {
            "CALL": "analyze_data",
            "ARGS": {
                "input_path": input_file,
                "output_path": f"output/analisis_{os.path.basename(input_file)}.json"
            }
        }

    return {"CALL": None, "ARGS": {}}

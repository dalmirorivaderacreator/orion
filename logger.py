import logging
import json
import os
from datetime import datetime

# Asegurar que existe el directorio de logs
os.makedirs("logs", exist_ok=True)

class JsonFormatter(logging.Formatter):
    """Formateador personalizado para logs en JSON"""
    def format(self, record):
        log_record = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName
        }

        # Agregar campos extra si existen
        if hasattr(record, 'extra_data'):
            log_record.update(record.extra_data)

        return json.dumps(log_record, ensure_ascii=False)

def setup_logger(name="orion_core"):
    """Configura y devuelve un logger robusto"""
    logger_instance = logging.getLogger(name)
    logger_instance.setLevel(logging.DEBUG)

    # Evitar duplicar handlers si se llama varias veces
    if logger_instance.handlers:
        return logger_instance

    # 1. File Handler (JSON estructurado para máquinas/análisis)
    file_handler = logging.FileHandler("logs/orion.log", encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(JsonFormatter())

    # 2. Console Handler (Texto limpio para humanos)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)

    logger_instance.addHandler(file_handler)
    logger_instance.addHandler(console_handler)

    return logger_instance

# Instancia global para importar fácilmente
logger = setup_logger()

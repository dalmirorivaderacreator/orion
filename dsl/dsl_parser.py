# dsl_parser.py
"""
Módulo para parsear y validar archivos DSL de ORION.
"""
import yaml
from dsl.dsl_spec import (
    ALLOWED_SOURCES,
    ALLOWED_OUTPUTS,
    ALLOWED_OPERATIONS,
    TYPE_CASTS,
)


class DSLValidationError(Exception):
    """Excepción personalizada para errores de validación del DSL."""

def load_dsl(path: str) -> dict:
    """Carga un YAML de pipeline y lo devuelve como dict."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise DSLValidationError(f"Error cargando DSL: {e}") from e


def validate_source(source: dict):
    """Valida la sección 'source' del DSL."""
    if source["type"] not in ALLOWED_SOURCES:
        raise DSLValidationError(f"source.type inválido: {source['type']}")


def validate_output(output: dict):
    """Valida la sección 'output' del DSL."""
    if output["type"] not in ALLOWED_OUTPUTS:
        raise DSLValidationError(f"output.type inválido: {output['type']}")


def validate_steps(steps: list):
    """Valida la lista de pasos del pipeline."""
    for step in steps:
        if len(step.keys()) != 1:
            raise DSLValidationError("Cada step debe tener solo una operación")

        op_name = list(step.keys())[0]
        if op_name not in ALLOWED_OPERATIONS:
            raise DSLValidationError(f"Operación inválida: {op_name}")

        # Validaciones específicas simples para v0.1:
        if op_name == "convert_type":
            to_type = step[op_name]["to"]
            if to_type not in TYPE_CASTS:
                raise DSLValidationError(f"Tipo invalido para convert_type: {to_type}")


def validate_dsl(dsl: dict):
    """Valida la estructura completa del DSL."""
    validate_source(dsl["source"])
    validate_steps(dsl["steps"])
    validate_output(dsl["output"])
    return True

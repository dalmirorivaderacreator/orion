# dsl_parser.py
import yaml
from .dsl_spec import (
    ALLOWED_SOURCES,
    ALLOWED_OUTPUTS,
    ALLOWED_OPERATIONS,
    TYPE_CASTS,
)

class DSLValidationError(Exception):
    pass


def load_dsl(path: str) -> dict:
    """Carga un YAML de pipeline y lo devuelve como dict."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise DSLValidationError(f"Error cargando DSL: {e}")


def validate_source(source: dict):
    if source["type"] not in ALLOWED_SOURCES:
        raise DSLValidationError(f"source.type inválido: {source['type']}")


def validate_output(output: dict):
    if output["type"] not in ALLOWED_OUTPUTS:
        raise DSLValidationError(f"output.type inválido: {output['type']}")


def validate_steps(steps: list):
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
    validate_source(dsl["source"])
    validate_steps(dsl["steps"])
    validate_output(dsl["output"])
    return True

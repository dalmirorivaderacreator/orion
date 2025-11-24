"""
Runner principal para ejecutar pipelines definidos en DSL.
"""
import sys
from dsl.dsl_parser import load_dsl
from dispatcher import dispatch
# Importar funciones para registro
# pylint: disable=unused-import
from functions import data_ops, file_ops


def run_pipeline(path):
    """Carga y ejecuta un pipeline desde un archivo YAML."""
    print(f"=== Ejecutando pipeline: {path} ===")

    dsl = load_dsl(path)
    pipeline = dsl["pipeline"]

    print(f"Pipeline: {pipeline['name']}")

    for step in pipeline["steps"]:
        action = step["action"]
        print(f"\n--- Ejecutando paso: {action} ---")

        args = {k: v for k, v in step.items() if k != "action"}

        result = dispatch(action, args)
        print("Resultado:", result)

    print("\n=== Pipeline finalizado ===")


def execute_plan(plan, context_manager=None):
    """
    Ejecuta un plan dinámico (lista de pasos) generado por el Planner.

    Args:
        plan (list): Lista de dicts con {"CALL": "...", "ARGS": ...}
        context_manager (ContextManager): Para actualizar contexto tras cada paso.
    """
    print(f"=== Ejecutando Plan Dinámico ({len(plan)} pasos) ===")

    results = []

    for i, step in enumerate(plan):
        action = step.get("CALL")
        args = step.get("ARGS", {})

        print(f"\n-> Paso {i+1}/{len(plan)}: {action}")

        try:
            # Ejecutar acción
            result = dispatch(action, args, context_manager)
            print(f"OK Resultado: {result}")
            results.append(result)

        except Exception as e:
            error_msg = f"ERROR en paso {i+1} ({action}): {str(e)}"
            print(error_msg)
            results.append(error_msg)
            # Detener ejecución en error crítico
            break

    print("\n=== Plan Finalizado ===")
    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python runner.py <ruta_pipeline_yaml>")
        sys.exit(1)

    run_pipeline(sys.argv[1])

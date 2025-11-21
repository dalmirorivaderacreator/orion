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

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python runner.py <ruta_pipeline_yaml>")
        sys.exit(1)

    run_pipeline(sys.argv[1])

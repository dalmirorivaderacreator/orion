import sys
from dsl.dsl_parser import load_dsl
from dispatcher import dispatch

def run_pipeline(path):
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

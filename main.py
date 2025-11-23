# pylint: disable=unused-import
from dotenv import load_dotenv
from llm_client import ask_orion
from dispatcher import dispatch
from logger import logger
from functions import data_ops, file_ops, system_ops, email_ops
from context import ContextManager
import database

# Cargar variables de entorno
load_dotenv()

print("=== Orion v0.1 conectado a Ollama ===")
logger.info("Sistema ORION iniciado")

from planner import HybridTaskPlanner
from runner import execute_plan

# ... imports ...

def main():
    """Bucle principal de la CLI"""
    # Inicializar DB
    database.init_db()
    
    # Mostrar mensaje de bienvenida con historial
    last_cmd = database.get_last_command()
    if last_cmd:
        print(f"👋 Bienvenido de nuevo. Tu último comando fue: '{last_cmd['command']}' ({last_cmd['timestamp']})")
    
    context = ContextManager()
    planner = HybridTaskPlanner()

    while True:
        try:
            user_input = input("\n>>> Tú: ")
            logger.info(
                "Input usuario: %s", user_input,
                extra={"extra_data": {"user_prompt": user_input}}
            )

            # 1. Intentar Planificación Compleja (Hybrid Planner)
            plan = planner.plan_task(user_input, context.context)
            
            if plan:
                logger.info("Plan complejo detectado: %s pasos", len(plan))
                results = execute_plan(plan, context)
                
                # Guardar en historial
                database.add_history(user_input, f"Plan ejecutado ({len(plan)} pasos)")
                continue

            # 2. Flujo Normal (Simple) - Obtener intención del LLM
            intent = ask_orion(user_input, context)

            # 3. Ejecutar función (y actualizar contexto)
            if intent["CALL"]:
                logger.info("Ejecutando %s", intent['CALL'])
                result = dispatch(intent["CALL"], intent["ARGS"], context)
                print(f">>> ORION: {result}")
                
                # Guardar en historial
                database.add_history(user_input, result)
                
                logger.info("Ejecución exitosa")

            else:
                print("\n[ORION]: No se pudo interpretar la instrucción.")
                logger.warning(
                    "No se pudo interpretar instrucción",
                    extra={"extra_data": {"prompt": user_input}}
                )

        except KeyboardInterrupt:
            logger.info("Sesión finalizada por usuario")
            print("\n¡Hasta luego!")
            break
        except Exception as e:
            logger.error("Error crítico en loop principal: %s", e, exc_info=True)
            print(f"\n[ERROR]: {e}")

if __name__ == "__main__":
    main()

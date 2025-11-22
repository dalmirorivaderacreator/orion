from llm_client import ask_orion
from dispatcher import dispatch
from logger import logger
# Importar funciones para registro
# pylint: disable=unused-import
from functions import data_ops, file_ops, system_ops
from context import ContextManager


print("=== Orion v0.1 conectado a Ollama ===")
logger.info("Sistema ORION iniciado")

def main():
    """Bucle principal de la CLI"""
    context = ContextManager()

    while True:
        try:
            user_input = input("\n>>> Tú: ")
            logger.info(
                "Input usuario: %s", user_input,
                extra={"extra_data": {"user_prompt": user_input}}
            )

            # 1. Obtener intención del LLM (con contexto)
            intent = ask_orion(user_input, context)

            # 2. Ejecutar función (y actualizar contexto)
            if intent["CALL"]:
                logger.info("Ejecutando %s", intent['CALL'])
                result = dispatch(intent["CALL"], intent["ARGS"], context)
                print(f">>> ORION: {result}")
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

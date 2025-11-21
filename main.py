from llm_client import ask_orion
from dispatcher import dispatch
from logger import logger

print("=== Orion v0.1 conectado a Ollama ===")
logger.info("Sistema ORION iniciado")

while True:
    try:
        prompt = input("Escribí tu prompt para Orion:\n> ")
        logger.info(
            "Input usuario: %s", prompt,
            extra={"extra_data": {"user_prompt": prompt}}
        )

        call_data = ask_orion(prompt)

        if call_data['CALL']:
            logger.info(
                "Ejecutando: %s", call_data['CALL'],
                extra={"extra_data": {"call": call_data}}
            )
            result = dispatch(call_data['CALL'], call_data['ARGS'])
            print("\n[ORION]:\n", result)
            logger.info("Ejecución exitosa")
        else:
            print("\n[ORION]: No se pudo interpretar la instrucción.")
            logger.warning(
                "No se pudo interpretar instrucción",
                extra={"extra_data": {"prompt": prompt}}
            )

    except KeyboardInterrupt:
        logger.info("Sesión finalizada por usuario")
        print("\n¡Hasta luego!")
        break
    except Exception as e:
        logger.error("Error crítico en loop principal: %s", e, exc_info=True)
        print(f"\n[ERROR]: {e}")

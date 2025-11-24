"""
ORION Main CLI Module

Provides the command-line interface for ORION, an AI-powered development assistant.
Handles user interaction, plugin initialization, and conversation management.
"""
# pylint: disable=unused-import
from dotenv import load_dotenv
from llm_client import ask_orion
from dispatcher import dispatch
from logger import logger
from functions import data_ops, file_ops, system_ops, email_ops
from context import ContextManager
from conversation import ConversationManager
import database

# Cargar variables de entorno
load_dotenv()

print("=== Orion v0.1 conectado a Ollama ===")
logger.info("Sistema ORION iniciado")

def main():
    """Bucle principal de la CLI"""
    # Inicializar DB
    # Inicializar DB
    database.init_db()

    # Inicializar sistema de plugins
    from core.plugins import PluginManager  # pylint: disable=import-outside-toplevel
    plugin_manager = PluginManager()
    loaded_count = plugin_manager.load_all_plugins()

    if loaded_count > 0:
        loaded_plugins = list(plugin_manager.plugins.keys())
        logger.info("Plugins cargados: %s", loaded_plugins)
        print(f"🔌 Plugins cargados: {', '.join(loaded_plugins)}")
    else:
        logger.info("No se cargaron plugins")

    # Mostrar mensaje de bienvenida con historial
    print("\n🌌 ORION - Asistente de Desarrollo Inteligente")
    print("---------------------------------------------")
    print("Ejemplos de uso:")
    print("  • 'Hola' (Conversación)")
    print("  • 'Creá proyecto web' (Automatización)")
    print("  • 'Ayuda' (Ver más comandos)")
    print("---------------------------------------------")

    last_cmd = database.get_last_command()
    if last_cmd:
        print(f"👋 Bienvenido de nuevo. Tu último comando fue: "
              f"'{last_cmd['command']}' ({last_cmd['timestamp']})")

    context = ContextManager()
    conversation = ConversationManager(context)

    while True:
        try:
            user_input = input("\n>>> Tú: ")
            logger.info(
                "Input usuario: %s", user_input,
                extra={"extra_data": {"user_prompt": user_input}}
            )

            # Procesar input con el ConversationManager
            response = conversation.process(user_input)

            # Manejar respuesta según tipo
            if response["type"] == "message":
                print(f">>> ORION: {response['response']}")

            elif response["type"] == "plan":
                print(f">>> ORION: {response['response']}")
                # Los resultados del plan ya se imprimieron en el runner

            elif response["type"] == "action":
                print(f">>> ORION: {response['result']}")

            elif response["type"] == "error":
                print(f">>> ORION: {response['response']}")
                logger.warning("No se pudo interpretar instrucción")

        except KeyboardInterrupt:
            logger.info("Sesión finalizada por usuario")
            print("\n¡Hasta luego!")
            break
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Error crítico en loop principal: %s", e, exc_info=True)
            print(f"\n[ERROR]: {e}")

if __name__ == "__main__":
    main()

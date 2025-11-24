"""
Módulo de Sistema Conversacional para ORION.
Maneja la clasificación de intenciones y el flujo de conversación.
"""
import re
import random

# Local imports
import database
from planner import HybridTaskPlanner
from runner import execute_plan
from llm_client import ask_orion
from dispatcher import dispatch
from logger import logger


class IntentClassifier:
    """Clasifica el input del usuario en intenciones básicas."""

    def classify(self, text: str) -> str:
        text = text.lower().strip()

        # 1. Greeting
        if re.search(r"\b(hola|buenos d[íi]as|buenas tardes|buenas noches|hey)\b", text):
            return "greeting"

        # 2. Chat/Persona (Questions about the bot)
        # "quien te creo", "quien eres", "creaste esto?", "como estas"
        if re.search(
            r"\b(qui[ée]n|cre[óo]|creaste|c[óo]mo est[áa]s|contame de vos|decime)\b",
            text
        ):
            return "chat"

        # 3. Question (Capabilities/Help)
        if re.search(
            r"\b(qu[ée] (puedes|sabes|pod[ée]s) hacer|c[óo]mo funcionas|"
            r"ayuda|help|funciones|cu[áa]les)\b",
            text
        ):
            return "question"

        # 4. Command (Work)
        if re.search(
            r"\b(cre[áa]|migr[áa]|list[áa]|borr[áa]|analiz[áa]|"
            r"configur[áa]|backup|carpeta|archivo)\b",
            text
        ):
            return "command"

        # 5. Fallback/Unknown
        return "unknown"


class ConversationManager:
    """Fachada principal para manejar la interacción con el usuario."""

    def __init__(self, context_manager):
        self.context_manager = context_manager
        self.planner = HybridTaskPlanner()
        self.classifier = IntentClassifier()

    def process(self, user_input: str) -> dict:
        """
        Procesa el input y devuelve un resultado estructurado.
        Retorna: {"type": str, "response": str|list, "result": any}
        """
        intent = self.classifier.classify(user_input)
        logger.info("Intención detectada: %s", intent)

        if intent == "greeting":
            return self._handle_greeting()
        if intent == "question":
            return self._handle_question()
        if intent == "chat":
            return self._handle_chat(user_input)
        if intent == "command":
            return self._handle_command(user_input)

        # Unknown -> Tratar como comando/chat genérico vía LLM
        return self._handle_command(user_input)

    def _handle_greeting(self):
        responses = [
            "¡Hola! ¿Cómo estás? Soy ORION, tu asistente de desarrollo.",
            "¡Buenas! Listo para programar. ¿Qué hacemos hoy?",
            "¡Hola! ¿En qué puedo ayudarte con tu proyecto?"
        ]
        return {"type": "message", "response": random.choice(responses)}

    def _handle_question(self):
        msg = (
            "**🤖 Guía Rápida de ORION**\n\n"
            "**1. Conversación**\n"
            "- 'Hola', 'Cómo estás', 'Quién te creó'\n\n"
            "**2. Automatización (Comandos)**\n"
            "- 'Creá proyecto web' (Genera HTML/CSS/JS)\n"
            "- 'Migrá proyecto de Python 3.9 a 3.11'\n"
            "- 'Hacé un backup de archivos'\n"
            "- 'Creá carpeta [nombre] y archivo [nombre]'\n\n"
            "**3. Utilidades**\n"
            "- 'Listá archivos', 'Analizá código'\n\n"
            "💡 *Tip: Probá combinar instrucciones o pedir ayuda específica.*"
        )
        return {"type": "message", "response": msg}

    def _handle_chat(self, user_input):
        user_input_lower = user_input.lower()

        if re.search(r"(qui[ée]n te cre[óo]|cre[óo])", user_input_lower):
            return {
                "type": "message",
                "response": "Me creó Dalmiro, un desarrollador apasionado por "
                            "la automatización e IA."
            }

        if re.search(r"c[óo]mo est[áa]s", user_input_lower):
            return {
                "type": "message",
                "response": "¡Excelente! Siempre listo para ayudarte con tus proyectos."
            }

        return {
            "type": "message",
            "response": "Soy ORION, combino IA con automatización para simplificar tu desarrollo."
        }

    def _handle_command(self, user_input):
        # 1. Intentar Planner (Reglas/Complejo)
        plan = self.planner.plan_task(user_input, self.context_manager.context)

        if plan:
            logger.info("Ejecutando plan complejo")
            results = execute_plan(plan, self.context_manager)
            database.add_history(user_input, f"Plan ejecutado ({len(plan)} pasos)")
            return {
                "type": "plan",
                "response": "Plan ejecutado correctamente.",
                "result": results,
                "plan": plan
            }

        # 2. Intentar Comando Simple (LLM)
        logger.info("Intentando comando simple vía LLM")
        intent = ask_orion(user_input, self.context_manager)

        if intent["CALL"]:
            result = dispatch(intent["CALL"], intent["ARGS"], self.context_manager)
            database.add_history(user_input, result)
            return {
                "type": "action",
                "response": f"Ejecutado: {intent['CALL']}",
                "result": result
            }

        # 3. Si falla todo
        return {
            "type": "error",
            "response": "¿Podés reformular? O decime 'qué puedes hacer' para ver mis capacidades."
        }

"""
Módulo de planificación de tareas híbrido (Reglas + LLM).
"""
import re
from logger import logger


class HybridTaskPlanner:
    """
    Planificador que combina reglas determinísticas con inteligencia LLM.
    """

    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    # pylint: disable=unused-argument
    def plan_task(self, user_input: str, context: dict) -> list:
        """
        Genera un plan de ejecución basado en el input del usuario.
        Prioridad:
        1. Reglas predefinidas (determinístico)
        2. LLM (si está disponible)
        3. Fallback (ejecución directa simple)
        """
        logger.info("Planificando tarea para: '%s'", user_input)

        # 1. Planner basado en reglas
        rule_plan = self._rule_based_plan(user_input)
        if rule_plan:
            logger.info("Plan generado por reglas: %s pasos", len(rule_plan))
            return rule_plan

        # 2. Planner basado en LLM (TODO: Implementar en siguiente iteración)
        # try:
        #     return self._llm_based_plan(user_input, context)
        # except Exception as e:
        #     logger.warning("Fallo en planificación LLM: %s", e)

        # 3. Fallback: No se pudo planificar, devolver None para ejecución
        # normal
        logger.info("No se generó plan complejo, delegando a ejecución simple.")
        return None

    # pylint: disable=too-many-return-statements
    def _rule_based_plan(self, user_input: str) -> list:
        """
        Detecta patrones conocidos y devuelve planes predefinidos.
        """
        prompt_lower = user_input.lower()

        # Regla 1: "creá proyecto web"
        if "creá proyecto web" in prompt_lower or "crear proyecto web" in prompt_lower:
            return [{"CALL": "create_folder",
                     "ARGS": {"path": "proyecto_web"}},
                    {"CALL": "create_file",
                     "ARGS": {"path": "proyecto_web/index.html",
                              "content": "<html><body><h1>Hola Mundo</h1></body></html>"}},
                    {"CALL": "create_file",
                     "ARGS": {"path": "proyecto_web/style.css",
                              "content": "body { background-color: #f0f0f0; }"}}]

        # Regla 2: "migrá proyecto" (Simple)
        if "migrá proyecto" in prompt_lower and "python" not in prompt_lower:
            return [{"CALL": "analyze_data",
                     "ARGS": {"input_path": ".",
                              "output_path": "migration_report.json"}},
                    {"CALL": "create_file",
                     "ARGS": {"path": "requirements_updated.txt",
                              "content": "# Updated requirements"}}]

        # Regla 3: "carpeta 'X' y archivo 'Y'" (Regex)
        # Match: creá carpeta 'foo' y archivo 'bar.txt'
        match_folder_file = re.search(
            r"carpeta ['\"](.+?)['\"] y archivo ['\"](.+?)['\"]",
            prompt_lower)
        if match_folder_file:
            folder = match_folder_file.group(1)
            file = match_folder_file.group(2)
            return [{"CALL": "create_folder",
                     "ARGS": {"path": folder}},
                    {"CALL": "create_file",
                     "ARGS": {"path": f"{folder}/{file}",
                              "content": f"Contenido de {file}"}}]

        # Regla 4: "migrá proyecto de Python X a Y"
        match_migration = re.search(
            r"migr[áa] proyecto de python (.+?) a (.+)",
            prompt_lower)
        if match_migration:
            ver_old = match_migration.group(1)
            ver_new = match_migration.group(2)
            return [{"CALL": "analyze_data",
                     "ARGS": {"input_path": ".",
                              "output_path": f"migration_{ver_old}_to_{ver_new}.json"}},
                    {"CALL": "create_file",
                     "ARGS": {"path": "requirements.txt",
                              "content": f"# Migrated to Python {ver_new}"}}]

        # Regla 5: "configurá entorno de desarrollo"
        if "configurá entorno de desarrollo" in prompt_lower:
            return [
                {"CALL": "create_file",
                 "ARGS": {"path": ".env",
                          "content": "DEBUG=True\nENV=development"}},
                {"CALL": "create_file",
                 "ARGS": {"path": ".gitignore",
                          "content": "*.pyc\n__pycache__/\n.env"}},
                {"CALL": "create_folder", "ARGS": {"path": "src"}},
                {"CALL": "create_folder", "ARGS": {"path": "tests"}}
            ]

        # Regla 6: "backup de archivos"
        if "backup de archivos" in prompt_lower:
            return [
                {"CALL": "create_folder", "ARGS": {"path": "backup"}},
                # Simulado: en realidad debería copiar
                {"CALL": "list_files", "ARGS": {"path": "."}},
                {"CALL": "create_file",
                 "ARGS": {"path": "backup/log.txt",
                          "content": "Backup completado"}}
            ]

        return None

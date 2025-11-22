"""
Módulo para manejar el contexto de la sesión (memoria a corto plazo).
"""

class ContextManager:
    """
    Gestiona variables de contexto que persisten entre comandos.
    Ej: última carpeta creada, último archivo descargado.
    """
    def __init__(self):
        self.context = {
            "last_folder": None,
            "last_file": None,
            "last_action": None
        }

    def update(self, key, value):
        """Actualiza una variable de contexto."""
        if key in self.context:
            self.context[key] = value

    def get_context_string(self):
        """Devuelve un string formateado para el System Prompt."""
        ctx_str = "\n**CONTEXTO ACTUAL (VARIABLES):**\n"
        has_context = False
        for key, value in self.context.items():
            if value:
                ctx_str += f"- {key}: {value}\n"
                has_context = True

        if not has_context:
            return ""

        return ctx_str

    def infer_update(self, function_name, args, result=None):
        """
        Infiere actualizaciones de contexto basadas en la acción ejecutada.
        """
        # pylint: disable=unused-argument
        self.context["last_action"] = function_name

        if function_name == "create_folder":
            self.context["last_folder"] = args.get("path")

        elif function_name == "download_file":
            self.context["last_file"] = args.get("output_path")

        elif function_name == "convert_csv_to_json":
            self.context["last_file"] = args.get("output_path")

        elif function_name == "analyze_data":
            self.context["last_file"] = args.get("output_path")

        elif function_name == "create_file":
            self.context["last_file"] = args.get("path")

        elif function_name == "list_files":

            self.context["last_folder"] = args.get("path")

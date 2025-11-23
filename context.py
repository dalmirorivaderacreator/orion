"""
Módulo para manejar el contexto de la sesión (memoria a corto plazo).
"""

import database


class ContextManager:
    """
    Gestiona variables de contexto que persisten entre comandos.
    Ej: última carpeta creada, último archivo descargado.
    """

    def __init__(self):
        # Inicializar DB y cargar contexto previo
        database.init_db()
        self.context = {
            "last_folder": None,
            "last_file": None,
            "last_action": None
        }
        # Cargar valores persistidos
        saved_context = database.load_context()
        self.context.update(saved_context)

    def update(self, key, value):
        """Actualiza una variable de contexto y la persiste."""
        if key in self.context:
            self.context[key] = value
            database.save_context({key: value})

    def get_context_string(self):
        """Devuelve un string formateado para el System Prompt."""
        if not any(self.context.values()):
            return ""

        ctx_str = "!!! ATENCIÓN: VARIABLES DE CONTEXTO ACTIVAS !!!\n"
        for key, value in self.context.items():
            if value:
                ctx_str += f"[{key.upper()} = '{value}']\n"
        ctx_str += "!!! FIN CONTEXTO !!!\n"

        return ctx_str

    def infer_update(self, function_name, args, result=None):
        """
        Infiere actualizaciones de contexto basadas en la acción ejecutada.
        """
        # pylint: disable=unused-argument, import-outside-toplevel
        from utils import normalize_path

        self.context["last_action"] = function_name

        if function_name == "create_folder":
            path = args.get("path")
            if path:
                self.context["last_folder"] = normalize_path(path)

        elif function_name == "download_file":
            path = args.get("output_path")
            if path:
                self.context["last_file"] = normalize_path(path)

        elif function_name == "convert_csv_to_json":
            path = args.get("output_path")
            if path:
                self.context["last_file"] = normalize_path(path)

        elif function_name == "analyze_data":
            path = args.get("output_path")
            if path:
                self.context["last_file"] = normalize_path(path)

        elif function_name == "create_file":
            path = args.get("path")
            if path:
                self.context["last_file"] = normalize_path(path)

        elif function_name == "list_files":
            path = args.get("path")
            if path:
                self.context["last_folder"] = normalize_path(path)

        # Persistir cambios automáticamente
        database.save_context(self.context)

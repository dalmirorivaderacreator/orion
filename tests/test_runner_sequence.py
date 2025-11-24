import unittest
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Local imports
# pylint: disable=wrong-import-position
import database
from context import ContextManager
from runner import execute_plan


class TestRunnerSequence(unittest.TestCase):
    def setUp(self):
        self.test_db = "test_runner.db"
        database.DB_NAME = self.test_db
        database.init_db()
        self.cm = ContextManager()

    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_execute_sequence(self):
        # Plan simulado: crear carpeta y luego listar
        plan = [
            {"CALL": "create_folder", "ARGS": {"path": "test_seq_folder"}},
            {"CALL": "list_files", "ARGS": {"path": "test_seq_folder"}}
        ]

        results = execute_plan(plan, self.cm)

        self.assertEqual(len(results), 2)
        self.assertIn("Carpeta creada", results[0])
        self.assertIn("Archivos en", results[1])

        # Verificar que el contexto se actualizó
        self.assertEqual(self.cm.context["last_folder"], "test_seq_folder")


if __name__ == '__main__':
    unittest.main()

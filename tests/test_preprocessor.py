import unittest
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Local imports
# pylint: disable=wrong-import-position
import database
from context import ContextManager
from llm_client import _preprocess_prompt


class TestPreprocessor(unittest.TestCase):
    def setUp(self):
        self.test_db = "test_preprocessor.db"
        database.DB_NAME = self.test_db
        database.init_db()
        self.cm = ContextManager()
        self.cm.context["last_folder"] = "test_folder"
        self.cm.context["last_file"] = "test_file.txt"

    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_folder_replacement(self):
        prompts = [
            ("listá archivos en esa carpeta", "listá archivos en test_folder"),
            ("ponelo ahí", "ponelo test_folder"),
            ("listá archivos en el directorio",
             "listá archivos en el directorio"),
            # No match pattern
            ("listá archivos en ese directorio", "listá archivos en test_folder")
        ]

        for original, expected in prompts:
            result = _preprocess_prompt(original, self.cm)
            self.assertEqual(result, expected)

    def test_file_replacement(self):
        prompts = [
            ("borrá ese archivo", "borrá test_file.txt"),
            ("procesá ese documento", "procesá test_file.txt")
        ]

        for original, expected in prompts:
            result = _preprocess_prompt(original, self.cm)
            self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()

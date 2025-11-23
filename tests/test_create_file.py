from context import ContextManager
from functions.file_ops import create_file
import unittest
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
# pylint: disable=wrong-import-position, import-error


class TestCreateFile(unittest.TestCase):
    def setUp(self):
        self.test_file = "test_output/test_file.txt"
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        if os.path.exists("test_output"):
            os.rmdir("test_output")

    def test_create_file_empty(self):
        result = create_file(self.test_file)
        self.assertTrue(os.path.exists(self.test_file))
        with open(self.test_file, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), "")
        self.assertIn("Archivo creado", result)

    def test_create_file_content(self):
        content = "Hello ORION"
        create_file(self.test_file, content)
        self.assertTrue(os.path.exists(self.test_file))
        with open(self.test_file, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), content)

    def test_context_update(self):
        cm = ContextManager()
        cm.infer_update("create_file", {"path": self.test_file}, "Created")
        self.assertEqual(cm.context["last_file"], self.test_file)


if __name__ == '__main__':
    unittest.main()

from functions.file_ops import create_file
from functions.system_ops import get_capabilities
import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
# pylint: disable=wrong-import-position, import-error


class TestRefinements(unittest.TestCase):
    def test_get_capabilities(self):
        caps = get_capabilities()
        self.assertIn("🚀 **Funciones Disponibles en ORION:**", caps)
        self.assertIn("create_file", caps)
        self.assertIn("get_capabilities", caps)

    def test_create_file_none_content(self):
        test_path = "test_none.txt"
        if os.path.exists(test_path):
            os.remove(test_path)

        # Should not raise error and create empty file
        create_file(test_path, None)

        self.assertTrue(os.path.exists(test_path))
        with open(test_path, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), "")

        if os.path.exists(test_path):
            os.remove(test_path)


if __name__ == '__main__':
    unittest.main()

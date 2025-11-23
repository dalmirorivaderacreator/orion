from context import ContextManager
from functions.system_ops import set_preference
from utils import normalize_path
import database
import unittest
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# pylint: disable=wrong-import-position, import-error


class TestPersistenceIntegration(unittest.TestCase):
    def setUp(self):
        self.test_db = "test_integration.db"
        database.DB_NAME = self.test_db
        database.init_db()

    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_path_normalization_windows(self):
        # Test stripping leading slash
        self.assertEqual(normalize_path("/folder/file.txt"), "folder/file.txt")
        self.assertEqual(
            normalize_path(".//folder//file.txt"),
            "folder/file.txt")

    def test_preference_persistence(self):
        # Set preference
        result = set_preference("favorite_color", "blue")
        self.assertIn("✅ Preferencia guardada", result)

        # Verify in DB
        val = database.get_preference("favorite_color")
        self.assertEqual(val, "blue")

    def test_context_persistence_across_instances(self):
        # Instance 1: Set context
        cm1 = ContextManager()
        cm1.update("last_folder", "secret_base")

        # Instance 2: Load context
        cm2 = ContextManager()
        self.assertEqual(cm2.context["last_folder"], "secret_base")


if __name__ == '__main__':
    unittest.main()

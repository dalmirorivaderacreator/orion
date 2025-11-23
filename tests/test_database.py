import unittest
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
# pylint: disable=wrong-import-position, import-error
import database

class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Usar base de datos de prueba
        self.test_db = "test_orion.db"
        database.DB_NAME = self.test_db
        database.init_db()

    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_save_and_load_context(self):
        ctx = {"last_folder": "test_dir", "last_file": "data.csv"}
        database.save_context(ctx)

        loaded = database.load_context()
        self.assertEqual(loaded["last_folder"], "test_dir")
        self.assertEqual(loaded["last_file"], "data.csv")

    def test_history_logging(self):
        database.add_history("create folder", "Success")

        last = database.get_last_command()
        self.assertIsNotNone(last)
        self.assertEqual(last["command"], "create folder")

    def test_preferences(self):
        database.set_preference("theme", "dark")
        val = database.get_preference("theme")
        self.assertEqual(val, "dark")

        val_none = database.get_preference("non_existent")
        self.assertIsNone(val_none)

if __name__ == '__main__':
    unittest.main()

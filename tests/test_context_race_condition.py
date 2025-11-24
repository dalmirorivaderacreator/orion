from context import ContextManager
import database
import unittest
import os
import sys
import time
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
# pylint: disable=wrong-import-position, import-error


class TestContextRaceCondition(unittest.TestCase):
    def setUp(self):
        self.test_db = "test_race.db"
        database.DB_NAME = self.test_db
        database.init_db()

    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_update_persistence(self):
        # 1. Initialize with old context
        cm = ContextManager()
        cm.update("last_folder", "old_folder")

        # Verify DB has old_folder
        self.assertEqual(database.load_context()["last_folder"], "old_folder")

        # 2. Update to new context (simulate create_folder)
        cm.infer_update("create_folder", {"path": "new_folder"})

        # Verify in-memory update
        self.assertEqual(cm.context["last_folder"], "new_folder")

        # Verify DB update immediately
        self.assertEqual(database.load_context()["last_folder"], "new_folder")

    def test_rapid_updates(self):
        cm = ContextManager()
        for i in range(10):
            folder_name = f"folder_{i}"
            cm.infer_update("create_folder", {"path": folder_name})
            # Verify immediate persistence
            loaded = database.load_context()
            self.assertEqual(loaded["last_folder"], folder_name)


if __name__ == '__main__':
    unittest.main()

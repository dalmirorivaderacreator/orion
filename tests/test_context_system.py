from context import ContextManager
import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
# pylint: disable=wrong-import-position, import-error


class TestContextSystem(unittest.TestCase):
    def test_context_update(self):
        cm = ContextManager()

        # Test 1: Create Folder
        cm.infer_update("create_folder", {"path": "test_folder"}, "Created")
        self.assertEqual(cm.context["last_folder"], "test_folder")
        self.assertEqual(cm.context["last_action"], "create_folder")

        # Test 2: List Files (should update last_folder)
        cm.infer_update("list_files", {"path": "another_folder"}, "Listed")
        self.assertEqual(cm.context["last_folder"], "another_folder")

        # Test 3: Download File
        cm.infer_update(
            "download_file", {
                "url": "http://x", "output_path": "data.csv"}, "Downloaded")
        self.assertEqual(cm.context["last_file"], "data.csv")

    def test_context_string_generation(self):
        cm = ContextManager()
        cm.update("last_folder", "my_project")

        ctx_str = cm.get_context_string()
        self.assertIn("CONTEXTO ACTUAL", ctx_str)
        self.assertIn("last_folder: my_project", ctx_str)


if __name__ == '__main__':
    unittest.main()

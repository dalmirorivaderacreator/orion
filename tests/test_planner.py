import unittest
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Local imports
# pylint: disable=wrong-import-position
from planner import HybridTaskPlanner


class TestHybridTaskPlanner(unittest.TestCase):
    def setUp(self):
        self.planner = HybridTaskPlanner()

    def test_rule_web_project(self):
        plan = self.planner.plan_task("creá proyecto web", {})
        self.assertIsNotNone(plan)
        self.assertEqual(len(plan), 3)
        self.assertEqual(plan[0]["CALL"], "create_folder")
        self.assertEqual(plan[1]["CALL"], "create_file")
        self.assertEqual(plan[2]["CALL"], "create_file")

    def test_rule_migration(self):
        plan = self.planner.plan_task("migrá proyecto", {})
        self.assertIsNotNone(plan)
        self.assertEqual(len(plan), 2)

    def test_regex_folder_file(self):
        plan = self.planner.plan_task(
            "creá carpeta 'mi_app' y archivo 'app.js'", {})
        self.assertIsNotNone(plan)
        self.assertEqual(len(plan), 2)
        self.assertEqual(plan[0]["ARGS"]["path"], "mi_app")
        self.assertEqual(plan[1]["ARGS"]["path"], "mi_app/app.js")

    def test_regex_migration_version(self):
        plan = self.planner.plan_task(
            "migrá proyecto de Python 3.9 a 3.11", {})
        self.assertIsNotNone(plan)
        self.assertEqual(len(plan), 2)
        self.assertIn("3.11", plan[1]["ARGS"]["content"])

    def test_setup_environment(self):
        plan = self.planner.plan_task("configurá entorno de desarrollo", {})
        self.assertIsNotNone(plan)
        self.assertEqual(len(plan), 4)
        self.assertEqual(plan[0]["ARGS"]["path"], ".env")

    def test_backup(self):
        plan = self.planner.plan_task("hacé un backup de archivos", {})
        self.assertIsNotNone(plan)
        self.assertEqual(len(plan), 3)

    def test_no_plan(self):
        plan = self.planner.plan_task("hola mundo", {})
        self.assertIsNone(plan)


if __name__ == '__main__':
    unittest.main()

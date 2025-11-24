import unittest
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Local imports
# pylint: disable=wrong-import-position
import database
from conversation import IntentClassifier, ConversationManager
from context import ContextManager


class TestConversation(unittest.TestCase):
    def setUp(self):
        self.classifier = IntentClassifier()
        # Mock DB for Manager
        database.DB_NAME = "test_conv.db"
        database.init_db()
        self.cm = ContextManager()
        self.manager = ConversationManager(self.cm)

    def tearDown(self):
        if os.path.exists("test_conv.db"):
            os.remove("test_conv.db")

    def test_classification(self):
        self.assertEqual(self.classifier.classify("hola"), "greeting")
        self.assertEqual(self.classifier.classify("qué puedes hacer"), "question")
        self.assertEqual(self.classifier.classify("creá una carpeta"), "command")
        self.assertEqual(self.classifier.classify("cómo estás"), "chat")
        self.assertEqual(self.classifier.classify("quien te creo?"), "chat")

    def test_classify_unknown(self):
        self.assertEqual(self.classifier.classify("blabla"), "unknown")

    def test_process_greeting(self):
        response = self.manager.process("Hola")
        self.assertEqual(response["type"], "message")
        # Check for either Hola or Buenas since response is random
        self.assertTrue("Hola" in response["response"] or "Buenas" in response["response"])

    def test_chat_response_creator(self):
        response = self.manager.process("quien te creo?")
        self.assertEqual(response["type"], "message")
        self.assertIn("Dalmiro", response["response"])

    def test_chat_response_status(self):
        response = self.manager.process("como estas")
        self.assertEqual(response["type"], "message")
        self.assertIn("Excelente", response["response"])

    def test_process_question(self):
        response = self.manager.process("ayuda")
        self.assertEqual(response["type"], "message")
        self.assertIn("Guía Rápida", response["response"])

    def test_command_execution(self):
        # Test simple command via LLM fallback (mocking LLM might be hard here without more setup,
        # but we can test the flow if we assume ask_orion works or mocks it.
        # For now, let's test a rule-based command which is deterministic)
        res = self.manager.process("creá proyecto web")
        self.assertEqual(res["type"], "plan")
        self.assertIsNotNone(res["result"])


if __name__ == '__main__':
    unittest.main()

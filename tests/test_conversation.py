import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from conversation import IntentClassifier, ConversationManager
from context import ContextManager
import database

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
        
    def test_greeting_response(self):
        res = self.manager.process("hola")
        self.assertEqual(res["type"], "message")
        # Check for either Hola or Buenas since response is random
        self.assertTrue("Hola" in res["response"] or "Buenas" in res["response"])

    def test_chat_response_creator(self):
        res = self.manager.process("quien te creo?")
        self.assertEqual(res["type"], "message")
        self.assertIn("Dalmiro", res["response"])

    def test_chat_response_status(self):
        res = self.manager.process("como estas")
        self.assertEqual(res["type"], "message")
        self.assertIn("Excelente", res["response"])

    def test_question_response(self):
        res = self.manager.process("cuales son tus funciones")
        self.assertEqual(res["type"], "message")
        self.assertIn("proyectos web", res["response"])

    def test_command_execution(self):
        # Test simple command via LLM fallback (mocking LLM might be hard here without more setup, 
        # but we can test the flow if we assume ask_orion works or mocks it. 
        # For now, let's test a rule-based command which is deterministic)
        res = self.manager.process("creá proyecto web")
        self.assertEqual(res["type"], "plan")
        self.assertIsNotNone(res["result"])

if __name__ == '__main__':
    unittest.main()

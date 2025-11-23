import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from functions.email_ops import send_email

class TestEmailOps(unittest.TestCase):
    @patch('functions.email_ops.smtplib.SMTP')
    @patch.dict(os.environ, {
        "SMTP_HOST": "smtp.test.com",
        "SMTP_PORT": "587",
        "SMTP_USER": "user@test.com",
        "SMTP_PASSWORD": "password"
    })
    def test_send_email_success(self, mock_smtp):
        # Setup mock
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Execute
        result = send_email("dest@test.com", "Subject", "Body")
        
        # Verify
        self.assertIn("✅ Correo enviado", result)
        mock_smtp.assert_called_with("smtp.test.com", 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_with("user@test.com", "password")
        mock_server.sendmail.assert_called_once()
        mock_server.quit.assert_called_once()

    def test_send_email_demo_mode(self):
        # Execute without env vars
        with patch.dict(os.environ, {}, clear=True):
            # Clean up log file if exists
            log_file = os.path.join("logs", "emails.log")
            if os.path.exists(log_file):
                os.remove(log_file)
                
            result = send_email("dest@test.com", "Subject", "Body")
            
            # Verify success message
            self.assertIn("✅ [MODO DEMO]", result)
            
            # Verify log file creation
            self.assertTrue(os.path.exists(log_file))
            with open(log_file, "r") as f:
                content = f.read()
                self.assertIn("TO: dest@test.com", content)
                self.assertIn("SUBJECT: Subject", content)

    def test_send_email_demo_mode_with_placeholders(self):
        # Execute with example/placeholder values
        with patch.dict(os.environ, {
            "SMTP_HOST": "smtp.example.com",
            "SMTP_PORT": "587",
            "SMTP_USER": "tu_usuario@example.com",
            "SMTP_PASSWORD": "password"
        }, clear=True):
            result = send_email("dest@test.com", "Subject", "Body")
            self.assertIn("✅ [MODO DEMO]", result)

    @patch('functions.email_ops.smtplib.SMTP')
    @patch.dict(os.environ, {
        "SMTP_HOST": "smtp.test.com",
        "SMTP_PORT": "587",
        "SMTP_USER": "user@test.com",
        "SMTP_PASSWORD": "password"
    })
    def test_send_email_failure(self, mock_smtp):
        # Setup mock to raise exception
        mock_smtp.side_effect = Exception("Connection failed")
        
        # Execute
        result = send_email("dest@test.com", "Subject", "Body")
        
        # Verify
        self.assertIn("❌ Error al enviar correo", result)
        self.assertIn("Connection failed", result)

if __name__ == '__main__':
    unittest.main()

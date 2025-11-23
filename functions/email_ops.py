"""
Operaciones de correo electrónico para ORION.
"""
import os
import smtplib
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from registry import register_function


def _send_demo_email(to: str, subject: str, body: str) -> str:
    """Simula el envío de un correo y lo registra en logs."""
    try:
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "emails.log")

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(
                f"[{timestamp}] TO: {to} | SUBJECT: {subject} | BODY: {body}\n")

        return f"✅ [MODO DEMO] Email simulado enviado a {to} (registrado en {log_file})"
    except Exception as e:
        return f"❌ Error en modo demo: {str(e)}"


@register_function(
    name="send_email",
    description="Envía un correo electrónico usando configuración SMTP",
    argument_types={"to": "str", "subject": "str", "body": "str"}
)
def send_email(to: str, subject: str, body: str) -> str:
    """
    Envía un email a la dirección especificada.
    Requiere variables de entorno: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD.
    """
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = os.environ.get("SMTP_PORT")
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")

    # Modo Demo: Si falta configuración o es la por defecto, simular envío
    is_configured = all([smtp_host, smtp_port, smtp_user, smtp_password])
    is_example = smtp_host == "smtp.example.com" or smtp_user == "tu_usuario@example.com"

    if not is_configured or is_example:
        return _send_demo_email(to, subject, body)

    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = to
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Conexión segura
        server = smtplib.SMTP(smtp_host, int(smtp_port))
        server.starttls()
        server.login(smtp_user, smtp_password)
        text = msg.as_string()
        server.sendmail(smtp_user, to, text)
        server.quit()

        return f"✅ Correo enviado exitosamente a {to}"

    except Exception as e:
        return f"❌ Error al enviar correo: {str(e)}"

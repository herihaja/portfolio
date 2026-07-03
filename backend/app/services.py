import logging
import smtplib
from email.message import EmailMessage

from .config import (
    CONTACT_EMAIL_TO,
    SMTP_FROM,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USE_TLS,
    SMTP_USER,
)
from .schemas import ContactCreate

logger = logging.getLogger(__name__)


def send_contact_email(payload: ContactCreate):
    logger.info(
        "Sending contact email for subject=%s email=%s",
        payload.subject,
        payload.email,
    )
    try:
        if not SMTP_HOST or not SMTP_USER or not SMTP_PASSWORD:
            raise RuntimeError("SMTP configuration is not fully set.")

        message = EmailMessage()
        message["Subject"] = f"New portfolio contact: {payload.subject}"
        message["From"] = SMTP_FROM
        message["To"] = CONTACT_EMAIL_TO
        message.set_content(
            f"New message from portfolio contact form:\n\n"
            f"Name: {payload.name}\n"
            f"Email: {payload.email}\n"
            f"Subject: {payload.subject}\n\n"
            f"Message:\n{payload.message}\n"
        )

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as smtp:
            if SMTP_USE_TLS:
                smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASSWORD)
            smtp.send_message(message)

    except Exception:
        logger.exception("Failed to send contact email")

from email.message import EmailMessage

import pytest

from app import services
from app.schemas import ContactCreate


class DummySMTP:
    def __init__(self, host, port, timeout=0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.started_tls = False
        self.logged_in = False
        self.sent_message = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def starttls(self):
        self.started_tls = True

    def login(self, user, password):
        self.logged_in = (user, password)

    def send_message(self, message: EmailMessage):
        self.sent_message = message


def test_send_contact_email_uses_smtp(monkeypatch):
    monkeypatch.setattr(services, "SMTP_HOST", "smtp.test.local")
    monkeypatch.setattr(services, "SMTP_PORT", 1025)
    monkeypatch.setattr(services, "SMTP_USER", "user@test.local")
    monkeypatch.setattr(services, "SMTP_PASSWORD", "password")
    monkeypatch.setattr(services, "SMTP_USE_TLS", True)
    monkeypatch.setattr(services, "SMTP_FROM", "from@test.local")
    monkeypatch.setattr(services, "CONTACT_EMAIL_TO", "to@test.local")

    smtp_instance = DummySMTP("smtp.test.local", 1025)

    class DummySMTPFactory:
        def __init__(self, instance):
            self.instance = instance

        def __call__(self, host, port, timeout=20):
            assert host == "smtp.test.local"
            assert port == 1025
            assert timeout == 20
            return self.instance

    monkeypatch.setattr("app.services.smtplib.SMTP", DummySMTPFactory(smtp_instance))

    payload = ContactCreate(
        name="Test User",
        email="test@example.com",
        subject="Hello",
        message="This is a test.",
    )

    services.send_contact_email(payload)

    assert smtp_instance.started_tls is True
    assert smtp_instance.logged_in == ("user@test.local", "password")
    assert smtp_instance.sent_message is not None
    assert smtp_instance.sent_message["To"] == "to@test.local"
    assert "New portfolio contact" in smtp_instance.sent_message["Subject"]

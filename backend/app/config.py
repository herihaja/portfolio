import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://portfolio:portfolio_pass@db:5432/portfolio",
)
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "1") in ("1", "true", "True", "yes", "Yes")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER or "no-reply@example.com")
CONTACT_EMAIL_TO = os.getenv("CONTACT_EMAIL_TO", "heriinfo@gmail.com")
ADMIN_LOGIN_USER = os.getenv("ADMIN_LOGIN_USER", "admin")
ADMIN_LOGIN_PASSWORD = os.getenv("ADMIN_LOGIN_PASSWORD", "")
RATE_LIMIT_REQUESTS = int(os.getenv("CONTACT_RATE_LIMIT_REQUESTS", "3"))
RATE_LIMIT_WINDOW = int(os.getenv("CONTACT_RATE_LIMIT_WINDOW_SECONDS", "60"))


ALLOWED_ORIGINS = {
    f"https://{os.getenv('DOMAIN_NAME', 'localhost')}",
    "http://localhost",
}

ADMIN_JWT_SECRET = os.getenv("ADMIN_JWT_SECRET")

if not ADMIN_JWT_SECRET:
    raise RuntimeError("ADMIN_JWT_SECRET is not configured")

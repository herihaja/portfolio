import os
import smtplib
import time
import logging

from collections import deque
from datetime import datetime, timezone
from email.message import EmailMessage
from threading import Lock
from typing import Deque, Dict

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field

from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

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

engine = create_engine(
    DATABASE_URL,
    future=True,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
Base = declarative_base()

rate_limit_state: Dict[str, Deque[float]] = {}
rate_limit_lock = Lock()
RATE_LIMIT_REQUESTS = int(os.getenv("CONTACT_RATE_LIMIT_REQUESTS", "5"))
RATE_LIMIT_WINDOW = int(os.getenv("CONTACT_RATE_LIMIT_WINDOW_SECONDS", "60"))


class ContactMessage(Base):
    __tablename__ = "contact_messages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(254), nullable=False)
    subject = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


class ContactCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    subject: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1, max_length=5000)

    class Config:
        anystr_strip_whitespace = True


app = FastAPI(title="portfolio-backend")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.on_event("startup")
def startup():
    for _ in range(10):
        try:
            Base.metadata.create_all(bind=engine)
            return
        except Exception:
            time.sleep(2)
    raise RuntimeError("Unable to connect to the database during startup.")


def get_client_ip(request: Request) -> str:
    return request.headers.get("x-real-ip") or request.client.host


def enforce_rate_limit(request: Request):
    ip = get_client_ip(request)
    now = time.time()

    with rate_limit_lock:
        queue = rate_limit_state.setdefault(ip, deque())
        while queue and queue[0] <= now - RATE_LIMIT_WINDOW:
            queue.popleft()

        if len(queue) >= RATE_LIMIT_REQUESTS:
            raise HTTPException(
                status_code=429,
                detail="Too many contact requests. Please try again later.",
            )

        queue.append(now)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def send_contact_email(payload: ContactCreate):
    logger.info(f"Sending contact email for: {payload.subject} from {payload.email}")
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
    
    

@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/version")
async def version():
    return {"service": "portfolio-backend", "version": "1.0.0"}

@app.post("/api/contact", status_code=status.HTTP_201_CREATED)
async def contact(
    request: Request,
    payload: ContactCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    enforce_rate_limit(request)

    contact = ContactMessage(
        name=payload.name,
        email=str(payload.email),
        subject=payload.subject,
        message=payload.message,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)

    background_tasks.add_task(send_contact_email, payload)

    return {"status": "ok", "message": "Contact request received."}

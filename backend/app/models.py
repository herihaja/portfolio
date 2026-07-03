from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text

from .database import Base


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


class VisitMessage(Base):
    __tablename__ = "visit_logs"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String(300), nullable=False)
    lang = Column(String(8), nullable=False)
    title = Column(String(200))
    referrer = Column(String(300))
    ip = Column(String(64))
    user_agent = Column(String(512))
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

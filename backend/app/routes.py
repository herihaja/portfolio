import logging
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from .config import (
    ADMIN_LOGIN_PASSWORD,
    ADMIN_LOGIN_USER,
)
from .database import get_db
from .models import ContactMessage, VisitMessage
from .schemas import (
    AdminLoginRequest,
    AdminLoginResponse,
    ContactCreate,
    ContactRead,
    VisitCreate,
    VisitRead,
)
from .services import send_contact_email
from .security import validate_origin, get_client_ip, enforce_rate_limit, require_admin
from .auth import create_admin_token

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/api/admin/login", response_model=AdminLoginResponse)
async def admin_login(payload: AdminLoginRequest):
    if (
        payload.username != ADMIN_LOGIN_USER
        or not ADMIN_LOGIN_PASSWORD
        or payload.password != ADMIN_LOGIN_PASSWORD
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_admin_token(payload.username)

    return {
        "token": token,
        "token_type": "bearer",
    }

@router.get("/api/health")
async def health():
    return {"status": "ok"}


@router.get("/api/version")
async def version():
    return {"service": "portfolio-backend", "version": "1.0.0"}


@router.get("/api/admin/messages", response_model=List[ContactRead])
async def admin_messages(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    return (
        db.query(ContactMessage)
        .order_by(ContactMessage.created_at.desc())
        .offset(skip)
        .limit(min(limit, 200))
        .all()
    )


@router.get("/api/admin/visits", response_model=List[VisitRead])
async def admin_visits(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    return (
        db.query(VisitMessage)
        .order_by(VisitMessage.created_at.desc())
        .offset(skip)
        .limit(min(limit, 200))
        .all()
    )


@router.post("/api/visit", status_code=status.HTTP_201_CREATED)
async def visit(
    request: Request,
    payload: VisitCreate,
    db: Session = Depends(get_db),
):
    visit = VisitMessage(
        path=payload.path,
        lang=payload.lang,
        title=payload.title,
        referrer=payload.referrer,
        ip=get_client_ip(request),
        user_agent=request.headers.get("user-agent"),
    )
    db.add(visit)
    db.commit()
    db.refresh(visit)

    return {"status": "ok"}


@router.post("/api/contact", status_code=status.HTTP_201_CREATED)
async def contact(
    request: Request,
    payload: ContactCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    validate_origin(request)
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

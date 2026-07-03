import time
from threading import Lock
from collections import deque
from typing import Deque, Dict

from .config import (
    RATE_LIMIT_REQUESTS,
    RATE_LIMIT_WINDOW,
    ALLOWED_ORIGINS
)

from fastapi import HTTPException, Request, status
from jose import JWTError

from .auth import verify_admin_token

data_store: Dict[str, Deque[float]] = {}
rate_limit_lock = Lock()

def validate_origin(request: Request):
    origin = request.headers.get("origin")

    if not origin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing origin header.",
        )

    if origin not in ALLOWED_ORIGINS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid origin.",
        )


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")

    if forwarded:
        return forwarded.split(",")[0].strip()

    return (
        request.headers.get("x-real-ip")
        or request.client.host
    )

def enforce_rate_limit(request: Request):
    ip = get_client_ip(request)
    now = time.time()

    with rate_limit_lock:
        queue = data_store.setdefault(ip, deque())
        while queue and queue[0] <= now - RATE_LIMIT_WINDOW:
            queue.popleft()

        if len(queue) >= RATE_LIMIT_REQUESTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many contact requests. Please try again later.",
            )

        queue.append(now)

def require_admin(request: Request) -> None:
    auth = request.headers.get("Authorization", "")

    if not auth.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth[7:].strip()

    try:
        verify_admin_token(token)
    except JWTError:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )

from datetime import datetime, timedelta, timezone
from jose import jwt
from .config import ADMIN_JWT_SECRET

ALGORITHM = "HS256"

def create_admin_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=60)

    payload = {
        "sub": username,
        "exp": expire,
    }

    return jwt.encode(payload, ADMIN_JWT_SECRET, algorithm=ALGORITHM)


def verify_admin_token(token: str):
    return jwt.decode(
        token,
        ADMIN_JWT_SECRET,
        algorithms=[ALGORITHM],
    )

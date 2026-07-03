from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class ContactCreate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True
    )
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    subject: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1, max_length=5000)

class ContactRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True
    )
    id: int
    name: str
    email: EmailStr
    subject: str
    message: str
    created_at: datetime


class VisitCreate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True
    )
    path: str
    lang: str
    title: Optional[str] = None
    referrer: Optional[str] = None


class VisitRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True
    )
    id: int
    path: str
    lang: str
    title: Optional[str] = None
    referrer: Optional[str] = None
    ip: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime


class AdminLoginRequest(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True
    )
    username: str
    password: str


class AdminLoginResponse(BaseModel):
    token: str
    token_type: str = "bearer"

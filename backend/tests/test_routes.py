import pytest
import os
from unittest.mock import patch
from fastapi import status

from app.schemas import ContactCreate, VisitCreate
from sqlalchemy import text

@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/api/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_version_endpoint(client):
    response = await client.get("/api/version")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["service"] == "portfolio-backend"


@pytest.mark.asyncio
async def test_contact_requires_origin_header(client):
    payload = {
        "name": "Alice",
        "email": "alice@example.com",
        "subject": "Hello",
        "message": "Hi there",
    }

    response = await client.post("/api/contact", json=payload)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Missing origin header."


@pytest.mark.asyncio
async def test_contact_blocks_unknown_origin(client):
    payload = {
        "name": "Alice",
        "email": "alice@example.com",
        "subject": "Hello",
        "message": "Hi there",
    }

    headers = {"origin": "http://evil.com"}
    response = await client.post("/api/contact", json=payload, headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Invalid origin."


@pytest.mark.asyncio
async def test_contact_enforces_rate_limit(client):
    payload = {
        "name": "Bob",
        "email": "bob@example.com",
        "subject": "Question",
        "message": "Testing rate limit",
    }

    headers = {"origin": "http://localhost"}

    with patch("app.routes.send_contact_email") as mock_send:
        mock_send.return_value = None

        first = await client.post(
            "/api/contact",
            json=payload,
            headers=headers,
        )

        assert first.status_code == status.HTTP_201_CREATED

        second = await client.post(
            "/api/contact",
            json=payload,
            headers=headers,
        )

        assert second.status_code == status.HTTP_201_CREATED

        third = await client.post(
            "/api/contact",
            json=payload,
            headers=headers,
        )

        assert third.status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.asyncio
async def test_visit_persists_visit(client, db_session):
    payload = {
        "path": "/projects",
        "lang": "en",
        "title": "Projects",
        "referrer": "http://localhost",
    }
    headers = {"user-agent": "pytest-agent", "x-real-ip": "203.0.113.8"}

    response = await client.post("/api/visit", json=payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["status"] == "ok"

    result = db_session.execute(
        text("SELECT path, lang, ip, user_agent FROM visit_logs")
    ).first()
    assert result == ("/projects", "en", "203.0.113.8", "pytest-agent")


@pytest.mark.asyncio
async def test_admin_login_returns_token(client):
    payload = {
        "username": os.getenv("ADMIN_LOGIN_USER"),
        "password": os.getenv("ADMIN_LOGIN_PASSWORD"),
    }
    response = await client.post("/api/admin/login", json=payload)

    assert response.status_code == status.HTTP_200_OK
    assert "token" in response.json()
    assert response.json()["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_admin_messages_requires_auth(client):
    response = await client.get("/api/admin/messages")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_admin_visits_requires_auth(client):
    response = await client.get("/api/admin/visits")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

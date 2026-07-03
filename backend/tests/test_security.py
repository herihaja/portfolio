import pytest
from fastapi import HTTPException

from app import auth, security
from app.security import get_client_ip


class DummyRequest:
    def __init__(self, headers=None, client_host="127.0.0.1"):
        self.headers = headers or {}
        self.client = type("Client", (), {"host": client_host})()


def test_validate_origin_allows_known_origin():
    request = DummyRequest(headers={"origin": "http://localhost"})
    security.validate_origin(request)


def test_validate_origin_rejects_missing_origin():
    request = DummyRequest(headers={})

    with pytest.raises(HTTPException) as exc:
        security.validate_origin(request)

    assert exc.value.status_code == 403
    assert exc.value.detail == "Missing origin header."


def test_validate_origin_rejects_unknown_origin():
    request = DummyRequest(headers={"origin": "http://evil.com"})

    with pytest.raises(HTTPException) as exc:
        security.validate_origin(request)

    assert exc.value.status_code == 403
    assert exc.value.detail == "Invalid origin."


def test_get_client_ip_prefers_x_forwarded_for():
    request = DummyRequest(headers={"x-forwarded-for": "203.0.113.1, 10.0.0.1"})
    assert get_client_ip(request) == "203.0.113.1"


def test_get_client_ip_uses_x_real_ip():
    request = DummyRequest(headers={"x-real-ip": "198.51.100.4"})
    assert get_client_ip(request) == "198.51.100.4"


def test_get_client_ip_falls_back_to_client_host():
    request = DummyRequest(headers={})
    assert get_client_ip(request) == "127.0.0.1"


def test_enforce_rate_limit_allows_requests_within_limit():
    request = DummyRequest(headers={"x-real-ip": "198.51.100.5"})
    security.RATE_LIMIT_WINDOW = 5
    security.RATE_LIMIT_REQUESTS = 2

    security.enforce_rate_limit(request)
    security.enforce_rate_limit(request)

    assert len(security.data_store[get_client_ip(request)]) == 2


def test_enforce_rate_limit_blocks_after_limit():
    request = DummyRequest(headers={"x-real-ip": "198.51.100.6"})
    security.RATE_LIMIT_WINDOW = 60
    security.RATE_LIMIT_REQUESTS = 1

    security.enforce_rate_limit(request)

    with pytest.raises(HTTPException) as exc:
        security.enforce_rate_limit(request)

    assert exc.value.status_code == 429


def test_require_admin_accepts_valid_token():
    token = auth.create_admin_token("admin")
    request = DummyRequest(headers={"Authorization": f"Bearer {token}"})
    security.require_admin(request)


def test_require_admin_rejects_missing_token():
    request = DummyRequest(headers={})

    with pytest.raises(HTTPException) as exc:
        security.require_admin(request)

    assert exc.value.status_code == 401


def test_require_admin_rejects_invalid_token():
    request = DummyRequest(headers={"Authorization": "Bearer bad-token"})

    with pytest.raises(HTTPException) as exc:
        security.require_admin(request)

    assert exc.value.status_code == 403

from app import auth


def test_create_and_verify_admin_token():
    token = auth.create_admin_token("admin")
    payload = auth.verify_admin_token(token)

    assert payload["sub"] == "admin"
    assert "exp" in payload

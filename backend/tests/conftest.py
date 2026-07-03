import os

os.environ.setdefault("ADMIN_JWT_SECRET", "test-secret")
os.environ.setdefault("ADMIN_LOGIN_USER", "admin")
os.environ.setdefault("ADMIN_LOGIN_PASSWORD", "secret")
os.environ.setdefault("CONTACT_RATE_LIMIT_REQUESTS", "2")
os.environ.setdefault("CONTACT_RATE_LIMIT_WINDOW_SECONDS", "5")
os.environ.setdefault("DOMAIN_NAME", "localhost")

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import database, security
from app.database import Base
from app.main import app as appx


TEST_SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    future=True,
)

TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
    future=True,
)

Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
async def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    appx.dependency_overrides[database.get_db] = override_get_db
    security.data_store.clear()

    transport = ASGITransport(app=appx)

    async with AsyncClient(
        transport=transport,
        base_url="http://localhost",
    ) as c:
        yield c

    appx.dependency_overrides.clear()

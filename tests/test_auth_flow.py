import re

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from abstract.base import Base
from app.main import app
from app.core.deps import get_db

TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture
def db_session():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        execution_options={"schema_translate_map": {"raw": None, "core": None, "staging": None, "analytics": None}},
    )
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_auth_flow(client):
    prints = []

    import app.services.auth_service as auth_mod
    original = auth_mod.LogEmailSender.send_code

    def fake(self, email, code):
        prints.append((email, code))

    auth_mod.LogEmailSender.send_code = fake

    r = client.post("/v1/auth/code", json={"email": "user@test.com"})
    assert r.status_code == 200
    assert r.json()["status"] == "sent"

    assert len(prints) == 1
    email, code = prints[0]
    assert email == "user@test.com"
    assert re.match(r"^\d{6}$", code)

    r = client.post("/v1/auth/verify", json={"email": "user@test.com", "code": code})
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["access_token"] is not None
    assert data["id_usuario"] == 1

    token = data["access_token"]

    r = client.get("/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    me = r.json()
    assert me["email"] == "user@test.com"
    assert me["nome"] == "user"

    auth_mod.LogEmailSender.send_code = original


def test_auth_invalid_code(client):
    import app.services.auth_service as auth_mod
    original = auth_mod.LogEmailSender.send_code
    auth_mod.LogEmailSender.send_code = lambda self, e, c: None

    client.post("/v1/auth/code", json={"email": "user@test.com"})
    r = client.post("/v1/auth/verify", json={"email": "user@test.com", "code": "000000"})
    assert r.status_code == 401

    auth_mod.LogEmailSender.send_code = original


def test_auth_no_token(client):
    r = client.get("/v1/auth/me")
    assert r.status_code in (401, 403)

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from abstract.base import Base
from abstract.models.core import Extracao, ExtracaoStatus
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


def _auth_header(client, email="user@test.com"):
    import app.services.auth_service as auth_mod
    auth_mod.override_email_sender(auth_mod.LogEmailSender())
    original = auth_mod.LogEmailSender.send_code
    codes = []

    def fake(self, email, code):
        codes.append(code)

    auth_mod.LogEmailSender.send_code = fake

    client.post("/v1/auth/code", json={"email": email})
    r = client.post("/v1/auth/verify", json={"email": email, "code": codes[0]})
    token = r.json()["access_token"]

    auth_mod.LogEmailSender.send_code = original
    return token


def test_list_extracao_empty(client):
    token = _auth_header(client)
    r = client.get("/v1/extracoes", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json() == []


def test_list_extracao_returns_user_extracoes(client, db_session):
    token1 = _auth_header(client, email="user1@test.com")
    token2 = _auth_header(client, email="user2@test.com")

    now = datetime.now(timezone.utc)
    e1 = Extracao(
        id_extracao=1,
        id_usuario=1,
        status=ExtracaoStatus.DONE,
        created_at=now,
    )
    e2 = Extracao(
        id_extracao=2,
        id_usuario=1,
        status=ExtracaoStatus.PENDING,
        created_at=now,
    )
    e3 = Extracao(
        id_extracao=3,
        id_usuario=2,
        status=ExtracaoStatus.DONE,
        created_at=now,
    )
    db_session.add_all([e1, e2, e3])
    db_session.commit()

    r1 = client.get("/v1/extracoes", headers={"Authorization": f"Bearer {token1}"})
    assert r1.status_code == 200
    data = r1.json()
    assert len(data) == 2
    ids1 = {d["id_extracao"] for d in data}
    assert ids1 == {1, 2}

    # Verify url field is present and nullable
    for d in data:
        assert "url" in d

    r2 = client.get("/v1/extracoes", headers={"Authorization": f"Bearer {token2}"})
    assert r2.status_code == 200
    r2_data = r2.json()
    assert len(r2_data) == 1
    assert r2_data[0]["id_extracao"] == 3
    # Verify url field for user2
    for d in r2_data:
        assert "url" in d


def test_list_extracao_limit(client, db_session):
    token = _auth_header(client)

    now = datetime.now(timezone.utc)
    for i in range(5):
        e = Extracao(
            id_extracao=i + 1,
            id_usuario=1,
            status=ExtracaoStatus.PENDING,
            created_at=now,
        )
        db_session.add(e)
    db_session.commit()

    r = client.get("/v1/extracoes?limit=3", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert len(r.json()) == 3


def test_list_extracao_unauthorized(client):
    r = client.get("/v1/extracoes")
    assert r.status_code in (401, 403)

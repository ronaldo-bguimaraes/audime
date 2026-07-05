"""Testes para o campo url na model Extracao.

Verifica que:
1. POST salva url e retorna nos endpoints GET
2. GET por id retorna url
3. url é nullable (registros antigos sem url)
"""

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
        execution_options={
            "schema_translate_map": {
                "raw": None,
                "core": None,
                "staging": None,
                "analytics": None,
            }
        },
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


class TestUrlField:
    """Testes para o campo url na model Extracao."""

    def test_create_extracao_saves_url(self, client):
        """POST salva url e retorna no GET list."""
        token = _auth_header(client)
        test_url = "https://www.sefaz.mt.gov.br/nfce/consultanfce?p=41160600000000000000651230000000001234567890"

        # POST
        r = client.post(
            "/v1/extracoes",
            json={"url": test_url},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 202
        post_data = r.json()
        assert "id_extracao" in post_data

        # GET list — verify url is returned
        r2 = client.get("/v1/extracoes", headers={"Authorization": f"Bearer {token}"})
        assert r2.status_code == 200
        extracoes = r2.json()
        assert len(extracoes) >= 1
        newest = extracoes[0]
        assert "url" in newest
        assert newest["url"] == test_url

    def test_get_extracao_by_id_returns_url(self, client):
        """GET por id retorna url."""
        token = _auth_header(client)
        test_url = "https://www.sefaz.mt.gov.br/nfce/consultanfce?p=123"

        r = client.post(
            "/v1/extracoes",
            json={"url": test_url},
            headers={"Authorization": f"Bearer {token}"},
        )
        post_data = r.json()
        id_extracao = post_data["id_extracao"]

        r2 = client.get(
            f"/v1/extracoes/{id_extracao}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r2.status_code == 200
        data = r2.json()
        assert data["url"] == test_url

    def test_url_nullable_for_old_records(self, client, db_session):
        """Extracao criado diretamente sem url deve retornar url: None."""
        token = _auth_header(client)

        # Create extraction directly via SQLAlchemy (no url)
        now = datetime.now(timezone.utc)
        e = Extracao(
            id_usuario=1,
            status=ExtracaoStatus.DONE,
            created_at=now,
            # note: no url passed
        )
        db_session.add(e)
        db_session.commit()

        # GET list — the record should have url: None
        r = client.get("/v1/extracoes", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        data = r.json()
        # Find our record
        for item in data:
            if item["id_extracao"] == e.id_extracao:
                assert "url" in item
                assert item["url"] is None
                break
        else:
            pytest.fail("Record not found")

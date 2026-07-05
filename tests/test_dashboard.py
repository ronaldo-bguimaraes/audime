"""Tests for dashboard endpoints — raw fallback and backfill.

TDD: these tests define expected behavior for the dashboard list endpoint
when the analytics table is empty (the current state of production).
"""

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from abstract.base import Base
from abstract.models.core import Extracao, ExtracaoStatus
from abstract.models.raw import Importacao, ItemNota, Nota
from abstract.models.analytics import NotaAnalytics, ItemNotaAnalytics
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


def _create_extracao_com_nota(db_session, id_extracao=1, id_usuario=1, status=ExtracaoStatus.DONE):
    """Helper: create an extraction with a raw nota (no analytics)."""
    now = datetime.now(timezone.utc)
    e = Extracao(
        id_extracao=id_extracao,
        id_usuario=id_usuario,
        status=status,
        created_at=now,
        url="https://example.com/nfce",
    )
    db_session.add(e)
    db_session.commit()

    imp = Importacao(
        id_importacao=id_extracao,
        storage_bucket="test",
        storage_key=f"test/{id_extracao}",
        storage_filename=f"file{id_extracao}.html",
        sha256="0" * 64,
        imported_at=now,
        id_extracao=id_extracao,
        id_usuario=id_usuario,
    )
    db_session.add(imp)
    db_session.commit()

    nota = Nota(
        id_nota=id_extracao,
        empresa="Test Empresa",
        chave="31200611222233300014455555555555555555555555",
        numero="123456",
        serie="1",
        emissao=now.date(),
        valor_total=100.50,
        qtd_total_itens=2,
        extra={},
        imported_at=now,
        id_usuario=id_usuario,
        id_importacao=imp.id_importacao,
    )
    db_session.add(nota)
    db_session.commit()

    for i in range(2):
        item = ItemNota(
            id_item_nota=id_extracao * 100 + i,
            item_codigo=str(i),
            item_descricao=f"Item {i}",
            item_quantidade=i + 1,
            item_tipo_unidade="UN",
            item_valor_unidade=10.0,
            item_valor_total=10.0 * (i + 1),
            id_nota=nota.id_nota,
            id_usuario=id_usuario,
        )
        db_session.add(item)
    db_session.commit()

    return e, imp, nota


# ── Tests for raw fallback in list endpoint ──────────────────────────


class TestDashboardListFallback:
    """Dashboard list endpoint — analytics only (no raw fallback)."""

    def test_listar_notas_with_analytics(self, client, db_session):
        """When analytics data exists, should return analytics data."""
        token = _auth_header(client)
        now = datetime.now(timezone.utc)

        _create_extracao_com_nota(db_session, id_extracao=1)

        nota_analytics = NotaAnalytics(
            id_nota_analytics=1,
            id_extracao=1,
            id_usuario=1,
            chave_acesso="31200611222233300014455555555555555555555555",
            empresa="Analytics Empresa",
            numero="123456",
            serie="1",
            emissao=now.date(),
            valor_total=200.75,
            qtd_total_itens=3,
            valid_from=now,
            is_current=True,
            id_importacao=1,
            id_nota_raw=1,
            processado_em=now,
        )
        db_session.add(nota_analytics)
        db_session.commit()

        item = ItemNotaAnalytics(
            id_item_analytics=1,
            id_nota_analytics=1,
            descricao="Item Analytics",
            quantidade=1.0,
            unidade="UN",
            valor_unitario=200.75,
            valor_total=200.75,
            processado_em=now,
        )
        db_session.add(item)
        db_session.commit()

        r = client.get("/v1/dashboard/notas", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 1
        assert data[0]["id_nota_analytics"] == 1
        assert data[0]["empresa"] == "Analytics Empresa"
        assert data[0]["valor_total"] == 200.75
        # version no longer returned
        assert "version" not in data[0]

    def test_listar_notas_raw_only_returns_empty(self, client, db_session):
        """When only raw data exists (no analytics), returns empty list."""
        token = _auth_header(client)
        _create_extracao_com_nota(db_session, id_extracao=1)

        r = client.get("/v1/dashboard/notas", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert r.json() == []

    def test_listar_notas_no_data_returns_empty_list(self, client, db_session):
        """User with no data should get empty list."""
        token = _auth_header(client)

        r = client.get("/v1/dashboard/notas", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert r.json() == []

    def test_listar_notas_mixed_data(self, client, db_session):
        """When some extractions have analytics, return only those."""
        token = _auth_header(client)
        now = datetime.now(timezone.utc)

        _create_extracao_com_nota(db_session, id_extracao=1)
        _create_extracao_com_nota(db_session, id_extracao=2)

        nota_analytics = NotaAnalytics(
            id_nota_analytics=2,
            id_extracao=2,
            id_usuario=1,
            chave_acesso="31200611222233300014455555555555555555555555",
            empresa="Analytics Empresa",
            numero="123456",
            serie="1",
            emissao=now.date(),
            valor_total=200.75,
            qtd_total_itens=3,
            valid_from=now,
            is_current=True,
            id_importacao=2,
            id_nota_raw=2,
            processado_em=now,
        )
        db_session.add(nota_analytics)
        db_session.commit()

        r = client.get("/v1/dashboard/notas", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 1
        assert data[0]["id_extracao"] == 2

    def test_listar_notas_only_own_user(self, client, db_session):
        """Should only return analytics notas belonging to authenticated user."""
        token1 = _auth_header(client, email="user1@test.com")
        token2 = _auth_header(client, email="user2@test.com")
        now = datetime.now(timezone.utc)

        _create_extracao_com_nota(db_session, id_extracao=1, id_usuario=1)

        nota_analytics = NotaAnalytics(
            id_nota_analytics=1, id_extracao=1, id_usuario=1,
            chave_acesso="x", empresa="User1 Only",
            numero="1", serie="1", emissao=now.date(),
            valor_total=100, qtd_total_itens=1,
            valid_from=now, is_current=True,
            id_importacao=1, id_nota_raw=1, processado_em=now,
        )
        db_session.add(nota_analytics)
        db_session.commit()

        r1 = client.get("/v1/dashboard/notas", headers={"Authorization": f"Bearer {token1}"})
        assert r1.status_code == 200
        assert len(r1.json()) == 1

        r2 = client.get("/v1/dashboard/notas", headers={"Authorization": f"Bearer {token2}"})
        assert r2.status_code == 200
        assert r2.json() == []

    def test_obter_nota_individual_only_analytics(self, client, db_session):
        """Individual nota endpoint only returns analytics data."""
        token = _auth_header(client)
        now = datetime.now(timezone.utc)
        _create_extracao_com_nota(db_session, id_extracao=1)

        r = client.get(
            "/v1/dashboard/notas/1",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 404

        nota_analytics = NotaAnalytics(
            id_nota_analytics=1, id_extracao=1, id_usuario=1,
            chave_acesso="x", empresa="Analytics Only",
            numero="1", serie="1", emissao=now.date(),
            valor_total=999.99, qtd_total_itens=1,
            valid_from=now, is_current=True,
            id_importacao=1, id_nota_raw=1, processado_em=now,
        )
        db_session.add(nota_analytics)
        db_session.commit()

        r = client.get(
            "/v1/dashboard/notas/1",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["empresa"] == "Analytics Only"
        assert data["valor_total"] == 999.99

    def test_obter_nota_individual_not_found(self, client, db_session):
        """Non-existent extraction should return 404."""
        token = _auth_header(client)

        r = client.get(
            "/v1/dashboard/notas/999",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 404


# ── Tests for backfill and reprocess url=None ────────────────────────


class TestDashboardBackfill:
    """Tests for the backfill mechanism to populate analytics."""

    def test_backfill_endpoint_exists(self, client, db_session):
        """POST /v1/extracoes/backfill should exist and return 202."""
        token = _auth_header(client)
        r = client.post(
            "/v1/extracoes/backfill",
            headers={"Authorization": f"Bearer {token}"},
        )
        # Should return 202 Accepted
        assert r.status_code == 202
        data = r.json()
        assert "enqueued" in data
        assert isinstance(data["enqueued"], int)

import os

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session

from abstract.base import Base

os.environ.setdefault("JWT_SECRET", "test-secret-not-for-production-use")
os.environ.setdefault("APP_ENV", "development")

ALEMBIC_CFG_PATH = os.path.join(os.path.dirname(__file__), "..", "alembic.ini")
TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5433/audime_test",
)

SCHEMAS = ["core", "raw", "staging", "analytics"]


# ── Session-scoped: engine + Alembic migrations (once) ──────────────


@pytest.fixture(scope="session")
def engine():
    eng = create_engine(TEST_DATABASE_URL)

    with eng.connect() as conn:
        for schema in SCHEMAS:
            conn.execute(text(f"DROP SCHEMA IF EXISTS {schema} CASCADE"))
        for schema in SCHEMAS:
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
        conn.commit()

    cfg = Config(ALEMBIC_CFG_PATH)
    cfg.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)
    command.upgrade(cfg, "head")

    with eng.connect() as conn:
        cols = {c["name"] for c in inspect(conn).get_columns("extracao", schema="core")}
        assert "url" in cols, f"url column missing after migration. Found: {cols}"

    yield eng
    eng.dispose()


# ── Function-scoped: db_session with TRUNCATE CASCADE teardown ───────


@pytest.fixture()
def db_session(engine):
    session = Session(bind=engine)
    try:
        yield session
    finally:
        session.close()
        _truncate_all(engine)


def _truncate_all(engine):
    with engine.connect() as conn:
        inspector = inspect(conn)
        for schema in SCHEMAS:
            tables = inspector.get_table_names(schema=schema)
            if tables:
                table_list = ", ".join(f"{schema}.{t}" for t in tables)
                conn.execute(text(f"TRUNCATE {table_list} CASCADE"))
        conn.commit()


# ── Function-scoped: FastAPI TestClient ──────────────────────────────


@pytest.fixture()
def client(db_session):
    from app.core.deps import get_db
    from app.main import app

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── Helper: auth header ──────────────────────────────────────────────


@pytest.fixture()
def auth_header(client):
    def _auth_header(email: str = "user@test.com") -> dict:
        import app.services.auth_service as auth_mod

        auth_mod.override_email_sender(auth_mod.LogEmailSender())
        original = auth_mod.LogEmailSender.send_code
        codes = []

        def fake(self, email, code):
            codes.append(code)

        auth_mod.LogEmailSender.send_code = fake

        client.post("/v1/auth/code", json={"email": email})
        r = client.post(
            "/v1/auth/verify", json={"email": email, "code": codes[0]}
        )
        data = r.json()
        token = data["access_token"]
        id_usuario = data["id_usuario"]

        auth_mod.LogEmailSender.send_code = original
        return {"Authorization": f"Bearer {token}"}, id_usuario

    return _auth_header

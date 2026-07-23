"""Testes de migrations do Alembic.

Valida que o sistema de migrações funciona corretamente contra PostgreSQL.
"""

import os

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

from abstract.base import Base
from abstract.models import (  # noqa: F401 — registra modelos no metadata
    AuthCode,
    Extracao,
    ExtracaoStep,
    Fatura,
    GastoCategoria,
    GastoMensal,
    Importacao,
    ItemNormalizado,
    ItemNota,
    Nota,
    NotaNormalizada,
    Transacao,
    Usuario,
)

ALEMBIC_CFG_PATH = os.path.join(os.path.dirname(__file__), "..", "alembic.ini")
TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5433/audime_test",
)

SCHEMAS = {"raw", "core", "staging", "analytics"}


def _drop_everything(engine):
    """Drop all schemas (with CASCADE), enum types, and recreate them empty."""
    with engine.connect() as conn:
        for schema in SCHEMAS:
            conn.execute(text(f"DROP SCHEMA IF EXISTS {schema} CASCADE"))
            conn.execute(text(f"CREATE SCHEMA {schema}"))
        # Drop any orphaned enum types in public schema
        conn.execute(text("""
            DO $$ DECLARE r RECORD;
            BEGIN
                FOR r IN (SELECT typname FROM pg_type WHERE typtype = 'e' AND typnamespace = 'public'::regnamespace) LOOP
                    EXECUTE 'DROP TYPE IF EXISTS ' || r.typname || ' CASCADE';
                END LOOP;
            END $$;
        """))
        conn.execute(text("DROP TABLE IF EXISTS core.alembic_version"))
        conn.commit()


@pytest.fixture
def fresh_engine():
    """Yields a PostgreSQL engine with all schemas wiped clean."""
    eng = create_engine(TEST_DATABASE_URL)
    _drop_everything(eng)
    yield eng
    eng.dispose()


@pytest.fixture
def alembic_cfg():
    cfg = Config(ALEMBIC_CFG_PATH)
    cfg.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)
    return cfg


DOMAIN_TABLES = {
    "usuario", "auth_code", "extracao",
    "importacao", "fatura", "transacao", "nota", "item_nota",
    "nota_normalizada", "item_normalizado",
    "gasto_mensal", "gasto_categoria",
    "extracao_step",
}


def test_upgrade_creates_tables(alembic_cfg, fresh_engine):
    """upgrade head cria todas as tabelas dos modelos."""
    with fresh_engine.connect() as conn:
        alembic_cfg.attributes["connection"] = conn
        command.upgrade(alembic_cfg, "head")

    inspector = inspect(fresh_engine)
    all_tables = set()
    for schema in ["core", "raw", "staging", "analytics"]:
        all_tables.update(inspector.get_table_names(schema=schema))

    assert "alembic_version" in all_tables or "alembic_version" in inspector.get_table_names()
    assert DOMAIN_TABLES.issubset(all_tables), (
        f"Tabelas faltando: {DOMAIN_TABLES - all_tables}"
    )


def test_upgrade_idempotent(alembic_cfg, fresh_engine):
    """Upgrade duas vezes seguidas não causa erro."""
    with fresh_engine.connect() as conn:
        alembic_cfg.attributes["connection"] = conn
        command.upgrade(alembic_cfg, "head")

    with fresh_engine.connect() as conn:
        alembic_cfg.attributes["connection"] = conn
        command.upgrade(alembic_cfg, "head")


def test_downgrade_idempotent(alembic_cfg, fresh_engine):
    """Downgrade + upgrade não causa erro."""
    with fresh_engine.connect() as conn:
        alembic_cfg.attributes["connection"] = conn
        command.upgrade(alembic_cfg, "head")

    with fresh_engine.connect() as conn:
        alembic_cfg.attributes["connection"] = conn
        command.downgrade(alembic_cfg, "base")

    with fresh_engine.connect() as conn:
        alembic_cfg.attributes["connection"] = conn
        command.upgrade(alembic_cfg, "head")


def test_migration_adds_url_column_to_extracao(alembic_cfg, fresh_engine):
    """Verifica que a migration add_url_to_extracao adiciona a coluna url."""
    with fresh_engine.connect() as conn:
        alembic_cfg.attributes["connection"] = conn
        command.upgrade(alembic_cfg, "head")

    inspector = inspect(fresh_engine)
    columns = {c["name"] for c in inspector.get_columns("extracao", schema="core")}
    assert "url" in columns


def test_models_metadata_is_complete():
    """Verifica que Base.metadata contém todos os modelos esperados."""
    expected_tables = {
        "usuario", "extracao", "auth_code", "extracao_step",
        "importacao", "fatura", "transacao", "nota", "item_nota",
        "nota_normalizada", "item_normalizado",
        "gasto_mensal", "gasto_categoria",
        "nota_analytics", "item_nota_analytics",
    }

    actual_tables = set(Base.metadata.tables.keys())
    actual_table_names = {t.split(".", 1)[1] if "." in t else t for t in actual_tables}

    assert expected_tables == actual_table_names, (
        f"Tabelas esperadas: {expected_tables - actual_table_names}\n"
        f"Tabelas extras: {actual_table_names - expected_tables}\n"
        f"Todas no metadata: {actual_tables}"
    )


def test_env_url_uses_config_option():
    """Verifica que o valor setado via set_main_option tem precedência."""
    cfg = Config(ALEMBIC_CFG_PATH)
    cfg.set_main_option("sqlalchemy.url", "sqlite:///./precedence_test.db")
    try:
        from alembic.env import get_database_url  # type: ignore

        import alembic.env as alembic_env_module  # type: ignore

        original_config = alembic_env_module.config
        alembic_env_module.config = cfg
        try:
            url = get_database_url()
            assert url == "sqlite:///./precedence_test.db", (
                f"Esperado sqlite:///./precedence_test.db, obtido {url}"
            )
        finally:
            alembic_env_module.config = original_config
    except ImportError:
        pass
    finally:
        try:
            os.remove("precedence_test.db")
        except FileNotFoundError:
            pass

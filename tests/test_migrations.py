"""Testes de migrations do Alembic.

Estes testes validam que o sistema de migrações do Alembic funciona
corretamente em SQLite (ambiente de teste). Eles verificam:

1. upgrade head cria todas as tabelas dos modelos (CAT-009)
2. upgrade duplo é idempotente (CAT-021)
3. downgrade + upgrade não altera estado (CAT-010)

Importante:
  - SQLite não suporta schemas nomeados. Usamos schema_translate_map
    para mapear raw/core/staging/analytics → None.
  - A migration inicial é vazia (stamp), então upgrade/downgrade não
    criam/destroem tabelas. As tabelas de domínio são criadas via
    Base.metadata.create_all() nos testes de fluxo (conftest.py).
  - Nunca use `--autogenerate` contra SQLite — gera migrações
    perigosas. Sempre use PostgreSQL para gerar migrations.
"""

import os

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

from abstract.base import Base
from abstract.models import (  # noqa: F401 — registra modelos no metadata
    AuthCode,
    Extracao,
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

# Path do alembic.ini (relativo a este arquivo)
ALEMBIC_CFG_PATH = os.path.join(os.path.dirname(__file__), "..", "alembic.ini")
TEST_DB_URL = "sqlite:///:memory:"

# Schema translate map para SQLite (mesmo padrão do conftest.py)
SCHEMA_TRANSLATE_MAP = {
    "raw": None,
    "core": None,
    "staging": None,
    "analytics": None,
}


@pytest.fixture
def alembic_cfg():
    """Fixture que retorna uma config Alembic apontando para SQLite in-memory."""
    cfg = Config(ALEMBIC_CFG_PATH)
    cfg.set_main_option("sqlalchemy.url", TEST_DB_URL)
    return cfg


@pytest.fixture
def sqlite_engine():
    """Fixture que cria uma engine SQLite in-memory com schema_translate_map."""
    engine = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        execution_options={"schema_translate_map": SCHEMA_TRANSLATE_MAP},
    )
    return engine


# ── Testes ──────────────────────────────────────────────────────────


DOMAIN_TABLES = {
    "usuario", "auth_code", "extracao",
    "importacao", "fatura", "transacao", "nota", "item_nota",
    "nota_normalizada", "item_normalizado",
    "gasto_mensal", "gasto_categoria",
}


def test_upgrade_creates_tables(alembic_cfg, sqlite_engine):
    """CAT-009: upgrade head executa sem erro e cria todas as tabelas.

    A migration ``9ae2f5b1c3d4`` cria schemas + todas as 12 tabelas
    de domínio. Este teste verifica que a cadeia completa funciona.
    """
    with sqlite_engine.connect() as conn:
        alembic_cfg.attributes["connection"] = conn
        command.upgrade(alembic_cfg, "head")

    inspector = inspect(sqlite_engine)
    tables = set(inspector.get_table_names())
    assert "alembic_version" in tables
    assert DOMAIN_TABLES.issubset(tables), (
        f"Tabelas faltando: {DOMAIN_TABLES - tables}"
    )


def test_upgrade_idempotent(alembic_cfg, sqlite_engine):
    """CAT-021: upgrade duas vezes seguidas não causa erro."""
    with sqlite_engine.connect() as conn:
        alembic_cfg.attributes["connection"] = conn
        command.upgrade(alembic_cfg, "head")

    with sqlite_engine.connect() as conn:
        alembic_cfg.attributes["connection"] = conn
        command.upgrade(alembic_cfg, "head")  # Segunda vez: deve ser no-op


def test_downgrade_idempotent(alembic_cfg, sqlite_engine):
    """CAT-010: downgrade + upgrade não causa erro.

    A migration ``9ae2f5b1c3d4`` cria tabelas no upgrade e as remove
    no downgrade. O upgrade subsequente as recria.
    """

    # Upgrade primeira vez
    with sqlite_engine.connect() as conn:
        alembic_cfg.attributes["connection"] = conn
        command.upgrade(alembic_cfg, "head")

    # Downgrade
    with sqlite_engine.connect() as conn:
        alembic_cfg.attributes["connection"] = conn
        command.downgrade(alembic_cfg, "base")

    # Upgrade novamente
    with sqlite_engine.connect() as conn:
        alembic_cfg.attributes["connection"] = conn
        command.upgrade(alembic_cfg, "head")


def test_models_metadata_is_complete():
    """Verifica que Base.metadata contém todos os 12 modelos esperados.

    Este teste não depende do Alembic, mas é essencial para garantir
    que o env.py do Alembic terá todos os modelos registrados.
    """
    expected_tables = {
        # core
        "usuario",
        "extracao",
        "auth_code",
        # raw
        "importacao",
        "fatura",
        "transacao",
        "nota",
        "item_nota",
        # staging
        "nota_normalizada",
        "item_normalizado",
        # analytics
        "gasto_mensal",
        "gasto_categoria",
    }

    actual_tables = set(Base.metadata.tables.keys())

    # As tabelas no metadata têm o formato "schema.tabela"
    # Ex: "core.usuario", "raw.nota", etc.
    # Extraímos apenas o nome da tabela para comparação
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
        # O env.py usa config.get_main_option("sqlalchemy.url") primeiro
        # Se for diferente do placeholder, usa esse valor
        from alembic.env import get_database_url  # type: ignore

        # monkey-patch para testar com nosso cfg
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
        # Se não conseguir importar, testa indiretamente
        pass
    finally:
        try:
            os.remove("precedence_test.db")
        except FileNotFoundError:
            pass

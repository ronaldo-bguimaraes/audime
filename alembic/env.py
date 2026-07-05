"""
Alembic env.py para o Audime.

Suporta PostgreSQL (produção/dev) e SQLite (testes/desenvolvimento).
Lê configurações de banco via app.core.config.Settings com fallback.

Ordem de precedência para URL:
  1. ALEMBIC_DB_URL (env var — override explícito)
  2. app.core.config.Settings (PostgreSQL em produção)
  3. sqlite:///./test.db (fallback para testes)
"""

import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Adiciona a raiz do projeto ao sys.path para imports funcionarem
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ── Importação de modelos ──────────────────────────────────────────
from abstract.base import Base
from abstract.models import (  # noqa: F401 — imports garantem registro no metadata
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

target_metadata = Base.metadata

# ── Config do Alembic ───────────────────────────────────────────────
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ── Schemas do Audime ───────────────────────────────────────────────
AUDIME_SCHEMAS = {"raw", "core", "staging", "analytics"}


def get_postgres_url() -> str:
    """Monta a URL de conexão PostgreSQL a partir das settings do projeto."""
    from app.core.config import settings
    from sqlalchemy import URL

    url = URL.create(
        drivername="postgresql+psycopg",
        username=settings.db_postgres_user,
        password=settings.db_postgres_password,
        host=settings.db_postgres_host,
        database=settings.db_postgres_name,
        port=settings.db_postgres_port,
    )
    return url.render_as_string(hide_password=True)


def get_database_url() -> str:
    """Retorna a URL do banco com base na ordem de precedência.

    1. Config file (sqlalchemy.url em alembic.ini ou setado programaticamente)
    2. ALEMBIC_DB_URL (env var)
    3. Settings do projeto (PostgreSQL)
    4. Fallback SQLite
    """
    # 1. Valor já configurado no alembic.ini ou setado programaticamente
    cfg_url = config.get_main_option("sqlalchemy.url")
    if cfg_url and cfg_url != "driver://user:pass@localhost/dbname":
        return cfg_url

    # 2. Env var
    env_url = os.environ.get("ALEMBIC_DB_URL")
    if env_url:
        return env_url

    # 3. Settings do projeto (PostgreSQL)
    try:
        return get_postgres_url()
    except Exception:
        return "sqlite:///./test.db"


def include_name(name, type_, parent_names):
    """Filtra schemas para incluir apenas os do Audime + default schema.

    Chamado pelo Alembic durante autogenerate para decidir quais schemas
    incluir na comparação. Essencial para evitar poluição de schemas do
    sistema (pg_catalog, information_schema, etc.).
    """
    if type_ == "schema":
        return name in AUDIME_SCHEMAS | {None}
    return True


def run_migrations_offline() -> None:
    """Gera SQL sem conectar no banco (modo offline)."""
    db_url = get_database_url()
    is_sqlite = "sqlite" in db_url

    context.configure(
        url=db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=not is_sqlite,
        include_name=include_name,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Conecta no banco e executa as migrations."""
    db_url = get_database_url()
    is_sqlite = "sqlite" in db_url

    config.set_main_option("sqlalchemy.url", db_url)

    # Verifica se uma conexão já foi fornecida via config.attributes
    # (útil para testes com SQLite in-memory)
    conn = config.attributes.get("connection", None)
    if conn is not None:
        # Usa a conexão fornecida externamente
        if is_sqlite:
            conn = conn.execution_options(
                schema_translate_map={
                    "raw": None,
                    "core": None,
                    "staging": None,
                    "analytics": None,
                }
            )
        context.configure(
            connection=conn,
            target_metadata=target_metadata,
            include_schemas=not is_sqlite,
            include_name=include_name,
            version_table_schema=None if is_sqlite else "core",
        )
        with context.begin_transaction():
            context.run_migrations()
    else:
        # Cria engine próprio
        connectable = engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

        with connectable.connect() as connection:
            # SQLite: aplica schema_translate_map para mapear schemas → None
            if is_sqlite:
                connection = connection.execution_options(
                    schema_translate_map={
                        "raw": None,
                        "core": None,
                        "staging": None,
                        "analytics": None,
                    }
                )

            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                include_schemas=not is_sqlite,
                include_name=include_name,
                version_table_schema=None if is_sqlite else "core",
            )

            with context.begin_transaction():
                context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

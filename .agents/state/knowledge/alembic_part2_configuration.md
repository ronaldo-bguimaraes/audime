# Alembic Part 2: Configuration and Setup

## Audime Context — Analysis of Current Setup

### Database Structure Today

**4 PostgreSQL schemas:**
- `raw` — raw data (invoices, transactions, notes, items)
- `core` — core entities (user, auth_code, extraction)
- `staging` — normalized data (normalized_note, normalized_item)
- `analytics` — analytical views (monthly_spending, category_spending)

**12 SQLAlchemy models** in `abstract/models/`:

| Model | Schema | Table | File |
|-------|--------|-------|------|
| Usuario | core | usuario | core.py |
| AuthCode | core | auth_code | core.py |
| Extracao | core | extracao | core.py |
| Importacao | raw | importacao | raw.py |
| Fatura | raw | fatura | raw.py |
| Transacao | raw | transacao | raw.py |
| Nota | raw | nota | raw.py |
| ItemNota | raw | item_nota | raw.py |
| NotaNormalizada | staging | nota_normalizada | staging.py |
| ItemNormalizado | staging | item_normalizado | staging.py |
| GastoMensal | analytics | gasto_mensal | analytics.py |
| GastoCategoria | analytics | gasto_categoria | analytics.py |

### How the DB is Connected

- **`abstract/engine.py`**: creates PostgreSQL engine via `sa.URL.create()` using `settings` from `app/core/config.py`
- **`abstract/base.py`**: `class Base(DeclarativeBase)` — root for all models
- **Tests (`tests/conftest.py`)**: use SQLite with `schema_translate_map` to map `raw → None`, `core → None`, etc., because SQLite does not support named schemas

### Current Problem

Today, migrations are manual via `scripts.sql` — a raw DDL file with `CREATE TABLE`, `ALTER TABLE`, and comments like "Migration: NFC-e Parser Enhancement (2026-06-30)". There is no:
- Versioning (which database version is running?)
- Downgrade (how to revert a change?)
- Automation (every change requires manually editing `scripts.sql`)
- Traceability (who changed what and when?)

---

## Step-by-Step: Setting Up Alembic in Audime

### Prerequisites

```bash
pip install alembic
# or add to pyproject.toml:
# "alembic>=1.14.0"
```

### 1. Initialize Environment

```bash
cd /home/ronaldo/Documents/GitHub/audime
alembic init alembic
```

This creates:
```
audime/
├── alembic.ini
└── alembic/
    ├── env.py
    ├── README
    ├── script.py.mako
    └── versions/
```

### 2. Configure `alembic.ini`

```ini
[alembic]
script_location = %(here)s/alembic
prepend_sys_path = .

# The URL will be overridden via env.py to use project settings
sqlalchemy.url = postgresql+psycopg://user:pass@localhost:5432/audime

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARNING
handlers = console

[logger_sqlalchemy]
level = WARNING

[logger_alembic]
level = INFO

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

> ⚠️ **Important:** the password in `sqlalchemy.url` needs `%` escaped as `%%` and special characters encoded with `urllib.parse.quote_plus`. But **we won't use** this hardcoded URL — we'll read from `settings` in `env.py`.

### 3. Configure `alembic/env.py` — The Heart of Configuration

The `env.py` must:
1. Import `Base.metadata` from all models (for autogenerate)
2. Configure the engine using project settings (PostgreSQL or SQLite for tests)
3. Enable `include_schemas=True` to detect schemas `raw`, `core`, `staging`, `analytics`
4. Set `compare_type=True` (already default) and optionally `compare_server_default`
5. For SQLite in tests, use `schema_translate_map` to translate schemas → None

Here is the complete `env.py` configuration:

```python
"""
Alembic env.py for Audime.

Supports PostgreSQL (production/dev) and SQLite (tests).
Reads database settings via app.core.config.Settings.
"""

import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool, create_engine

# Add the root directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Import Base with all registered models
from abstract.base import Base
from abstract.models import *  # noqa: F401, F403 — registers all models in Base.metadata

# Alembic config
config = context.config

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# target_metadata = all models
target_metadata = Base.metadata

# --- Utilities ---

def get_postgres_url() -> str:
    """Build PostgreSQL connection URL from project settings."""
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
    return url.render_as_string(hide_password=False)


def include_name(name, type_, parent_names):
    """Filter schemas to include only Audime schemas + default schema."""
    if type_ == "schema":
        return name in (None, "raw", "core", "staging", "analytics")
    return True


def run_migrations_offline() -> None:
    """Generate SQL without connecting to the database (offline mode)."""
    context.configure(
        url=get_postgres_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        include_name=include_name,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Connect to the database and run migrations."""

    db_driver = os.environ.get("ALEMBIC_DB_DRIVER", "postgresql")

    if db_driver == "sqlite":
        db_url = os.environ.get("ALEMBIC_DB_URL", "sqlite:///./test.db")
        connectable = create_engine(
            db_url,
            connect_args={"check_same_thread": False},
            execution_options={
                "schema_translate_map": {
                    "raw": None, "core": None,
                    "staging": None, "analytics": None,
                }
            },
        )
    else:
        connectable = engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            url=get_postgres_url(),
        )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            include_name=include_name,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

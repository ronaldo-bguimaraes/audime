#!/bin/sh
set -e

echo "Running database migrations..."

# Try normal upgrade first
if alembic upgrade head; then
    echo "Migrations complete."
else
    echo "Upgrade failed, checking if database is already up to date..."

    # If domain tables exist, this is an old DB with a broken migration chain.
    # Stamp head to sync the version, then re-run upgrade (should be no-op).
    HAS_TABLES=$(python -c "
import sys; sys.path.insert(0, '.')
from sqlalchemy import create_engine, inspect
from app.core.config import settings
from sqlalchemy import URL

url = URL.create(
    drivername='postgresql+psycopg',
    username=settings.db_postgres_user,
    password=settings.db_postgres_password,
    host=settings.db_postgres_host,
    database=settings.db_postgres_name,
    port=settings.db_postgres_port,
)
eng = create_engine(url.render_as_string(hide_password=False))
with eng.connect() as c:
    tables = inspect(c).get_table_names(schema='core')
    print('yes' if 'usuario' in tables else 'no')
eng.dispose()
" 2>/dev/null || echo "no")

    if [ "$HAS_TABLES" = "yes" ]; then
        echo "Existing database detected, stamping to current version..."
        alembic stamp head
        alembic upgrade head
        echo "Migrations complete (stamped)."
    else
        echo "ERROR: Migration failed and no existing tables found."
        exit 1
    fi
fi

exec "$@"

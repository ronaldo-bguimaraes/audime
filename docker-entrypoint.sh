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
from sqlalchemy import create_engine, inspect
import os
url = os.environ.get('ALEMBIC_DB_URL', os.environ.get('DATABASE_URL', ''))
eng = create_engine(url)
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

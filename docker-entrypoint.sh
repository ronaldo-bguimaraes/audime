#!/bin/sh
set -e

echo "Running database migrations..."

# Try normal upgrade first
if alembic upgrade head; then
    echo "Migrations complete."
else
    echo "Upgrade failed, checking if database is already up to date..."

    HAS_TABLES=$(python scripts/stamp_migration.py 2>/dev/null || echo "no")

    if [ "$HAS_TABLES" = "yes" ]; then
        echo "Existing database detected, version stamped."
        alembic upgrade head
        echo "Migrations complete."
    else
        echo "ERROR: Migration failed and no existing tables found."
        exit 1
    fi
fi

exec "$@"

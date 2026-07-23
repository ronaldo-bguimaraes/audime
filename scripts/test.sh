#!/usr/bin/env bash
# scripts/test.sh — Start a temporary PostgreSQL via Docker, run tests, tear down.
set -euo pipefail

COMPOSE_FILE="docker-compose.test.yml"

cleanup() {
    echo "→ Tearing down test database..."
    docker compose -f "$COMPOSE_FILE" down -v --remove-orphans 2>/dev/null || true
}
trap cleanup EXIT

echo "→ Starting test PostgreSQL..."
docker compose -f "$COMPOSE_FILE" up -d --wait

echo "→ Running tests..."
VENV_PYTEST="$(pwd)/.venv/bin/pytest"
exec "$VENV_PYTEST" "$@"

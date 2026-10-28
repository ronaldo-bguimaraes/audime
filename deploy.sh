#!/bin/sh
set -e

[ ! -f .env ] && echo "Missing .env — copy .env.example to .env first" && exit 1

if ! grep -qE '^\s*CLOUDFLARE_TUNNEL_TOKEN\s*=\s*"?[^"[:space:]]+' .env; then
  echo "Missing CLOUDFLARE_TUNNEL_TOKEN in .env — the tunnel will not come up" >&2
  exit 1
fi

if ! grep -qE '^\s*APP_ENV\s*=\s*"?production' .env; then
  echo "WARNING: APP_ENV is not 'production' — verification emails are only logged, not sent" >&2
fi

docker compose build backend worker web
docker compose up -d redis backend worker web cloudflared
docker compose ps

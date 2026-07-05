#!/bin/sh
set -e

[ ! -f .env ] && echo "Missing .env — copy .env.example to .env first" && exit 1

docker compose build backend worker web
docker compose up -d backend worker web
docker compose ps

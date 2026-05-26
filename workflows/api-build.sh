#!/usr/bin/env bash

set -euo pipefail

npm ci

echo "Building schemas..."
npm run build -w @audime/schemas

echo "Building api..."
npm run build -w @audime/api

echo "Done"

#!/usr/bin/env bash

set -euo pipefail

echo "Building schemas..."
npm run build -w @audime/schemas

echo "Building api..."
npm run build -w @audime/api

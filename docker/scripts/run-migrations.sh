#!/usr/bin/env sh
set -euo pipefail

if [ -z "${DATABASE_URL:-}" ]; then
  echo "DATABASE_URL environment variable must be set" >&2
  exit 1
fi

alembic upgrade head

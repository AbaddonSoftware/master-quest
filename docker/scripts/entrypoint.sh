#!/usr/bin/env sh
set -e

if [ -z "$DATABASE_URL" ]; then
  echo "DATABASE_URL environment variable must be set" >&2
  exit 1
fi

exec gunicorn "wsgi:app" -b 0.0.0.0:${PORT:-8080} -w 4 --threads 4 --timeout 30

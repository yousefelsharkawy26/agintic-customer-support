#!/usr/bin/env bash
set -euo pipefail

WORKERS="${WORKER_COUNT:-4}"

echo "Starting Customer Support API — $WORKERS workers"

exec uvicorn apps.api.main:app \
    --host 0.0.0.0 \
    --port 8080 \
    --workers "$WORKERS" \
    --log-level info \
    --proxy-headers \
    --forwarded-allow-ips '*'

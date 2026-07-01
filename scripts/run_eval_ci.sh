#!/usr/bin/env bash
set -euo pipefail

# CI eval runner — runs golden QA eval, checks regression against baseline.
# Usage: ./scripts/run_eval_ci.sh [--update-baseline]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"

echo "=== Eval CI ==="
uv run python -m apps.api.eval.ci_runner "$@"

echo "=== Eval CI complete ==="

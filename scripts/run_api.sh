#!/usr/bin/env bash
# Run FastAPI locally on port 8040 (override with API_PORT).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/services/api"
PORT="${API_PORT:-8040}"
if [[ -d .venv ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi
exec uvicorn skiplanner_api.main:app --reload --host "${API_HOST:-0.0.0.0}" --port "$PORT"

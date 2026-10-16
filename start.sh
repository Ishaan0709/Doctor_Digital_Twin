#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(pwd)"
export PYTHONDONTWRITEBYTECODE=1

if [[ -x "$ROOT/.venv/bin/python" ]]; then
  VENV="$ROOT/.venv"
elif [[ -x "$ROOT/../.venv/bin/python" ]]; then
  VENV="$ROOT/../.venv"
else
  echo "No virtual environment found. Run setup.sh first."
  exit 1
fi

if [[ ! -f "$ROOT/web/dist/index.html" ]]; then
  echo "Frontend build not found. Run setup.sh first."
  exit 1
fi

if command -v open >/dev/null 2>&1; then
  open "http://localhost:8000"
elif command -v xdg-open >/dev/null 2>&1; then
  xdg-open "http://localhost:8000" >/dev/null 2>&1 || true
fi

exec "$VENV/bin/python" -m uvicorn backend.app:app --host 127.0.0.1 --port 8000

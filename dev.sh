#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(pwd)"

if [[ -x "$ROOT/.venv/bin/python" ]]; then
  VENV="$ROOT/.venv"
elif [[ -x "$ROOT/../.venv/bin/python" ]]; then
  VENV="$ROOT/../.venv"
else
  echo "No virtual environment found. Run setup.sh first."
  exit 1
fi

exec "$VENV/bin/python" "$ROOT/scripts/dev_server.py"

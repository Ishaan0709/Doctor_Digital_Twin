#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(pwd)"

if ! command -v node >/dev/null 2>&1; then
  echo "Node.js is required. Install it from https://nodejs.org and run setup.sh again."
  exit 1
fi

if [[ -x "$ROOT/.venv/bin/python" ]]; then
  VENV="$ROOT/.venv"
elif [[ -x "$ROOT/../.venv/bin/python" ]]; then
  VENV="$ROOT/../.venv"
else
  python3 -m venv "$ROOT/.venv"
  VENV="$ROOT/.venv"
fi

echo "Using $VENV"
"$VENV/bin/python" -m pip install --upgrade pip
"$VENV/bin/python" -m pip install -r "$ROOT/requirements.txt"
(cd "$ROOT/web" && npm install && npm run build)

if [[ ! -f "$ROOT/.env" ]]; then
  cp "$ROOT/.env.example" "$ROOT/.env"
  echo "Created .env from .env.example. Add your OPENAI_API_KEY."
else
  echo ".env already exists and was left unchanged."
fi

echo "Setup complete. Next, run ./start.sh"

#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONUTF8=1
if [[ ! -x .venv/bin/python ]]; then
  echo "Missing .venv. Run scripts/setup.sh first." >&2
  exit 1
fi
if command -v ss >/dev/null 2>&1 && ss -ltn | grep -q ':8000 '; then
  echo "Port 8000 is already in use." >&2
  exit 1
fi
echo "Open http://127.0.0.1:8000"
echo "Stop with Ctrl+C"
exec .venv/bin/python -m uvicorn natalia.api:create_app --factory --host 127.0.0.1 --port 8000 --workers 1

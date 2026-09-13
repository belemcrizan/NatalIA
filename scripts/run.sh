#!/usr/bin/env bash
# NatalIA startup script for Linux and macOS.
# Starts NatalIA on loopback using the project virtual environment.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"

PORT="${PORT:-8000}"
HOST="${HOST:-127.0.0.1}"
WORKERS="${WORKERS:-1}"

# Parse optional arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --port|-p)
      PORT="$2"
      shift 2
      ;;
    --host|-h)
      HOST="$2"
      shift 2
      ;;
    --workers|-w)
      WORKERS="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1" >&2
      echo "Usage: ./scripts/run.sh [--port <port>] [--host <host>] [--workers <n>]" >&2
      exit 1
      ;;
  esac
done

export PYTHONUTF8=1
VENV_PYTHON="$ROOT/.venv/bin/python"

if [[ ! -x "$VENV_PYTHON" ]]; then
  echo "Error: Virtual environment not found at $VENV_PYTHON" >&2
  echo "Please run ./scripts/setup.sh first." >&2
  exit 1
fi

# Check port availability using python socket test
if ! "$VENV_PYTHON" -c "import socket; s = socket.socket(); s.bind(('$HOST', $PORT)); s.close()" 2>/dev/null; then
  echo "" >&2
  echo "============================================================" >&2
  echo "Error: Port $PORT on $HOST is already in use." >&2
  echo "To start NatalIA on another port, use:" >&2
  echo "    ./scripts/run.sh --port $((PORT + 1))" >&2
  echo "Or stop the process currently using port $PORT and retry." >&2
  echo "============================================================" >&2
  echo "" >&2
  exit 1
fi

echo ""
echo "============================================================"
echo " NatalIA Verification Workbench"
echo " Web Interface: http://${HOST}:${PORT}"
echo " API Ready:     http://${HOST}:${PORT}/health/ready"
echo " Project Root:  ${ROOT}"
echo " To stop the server, press Ctrl + C in this terminal window."
echo "============================================================"
echo ""

exec "$VENV_PYTHON" -m uvicorn natalia.api:create_app --factory --host "$HOST" --port "$PORT" --workers "$WORKERS"

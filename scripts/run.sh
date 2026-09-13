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

if [[ "$WORKERS" != "1" ]]; then
  echo "Error: this local release requires --workers 1 (single uvicorn process)." >&2
  exit 1
}

export PYTHONUTF8=1
VENV_PYTHON="$ROOT/.venv/bin/python"

if [[ ! -x "$VENV_PYTHON" ]]; then
  echo "Error: Virtual environment not found at $VENV_PYTHON" >&2
  echo "Please run ./scripts/setup.sh first." >&2
  exit 1
fi

# Check port availability using python socket test
BIND_STATUS="$("$VENV_PYTHON" -c "from natalia.cli import classify_port; print(classify_port('$HOST', int('$PORT')))" || true)"
if [[ "$BIND_STATUS" == "invalid_host" ]]; then
  echo "Error: cannot bind $HOST:$PORT (invalid host or permission). Not an occupied-port error." >&2
  exit 1
fi
if [[ "$BIND_STATUS" != "free" ]]; then
  echo "" >&2
  echo "============================================================" >&2
  echo "Error: Port $PORT on $HOST is already in use." >&2
  echo "To start NatalIA on another port, use:" >&2
  echo "    ./scripts/run.sh --port $((PORT + 1))" >&2
  echo "============================================================" >&2
  echo "" >&2
  exit 1
fi

echo ""
echo "============================================================"
echo " NatalIA Verification Workbench"
echo " Starting at:   http://${HOST}:${PORT}"
echo " Readiness:     GET http://${HOST}:${PORT}/health/ready (URL print is not readiness)"
echo " Project Root:  ${ROOT}"
echo " To stop the server, press Ctrl + C in this terminal window."
echo "============================================================"
echo ""

exec "$VENV_PYTHON" -m uvicorn natalia.api:create_app --factory --host "$HOST" --port "$PORT" --workers "$WORKERS"

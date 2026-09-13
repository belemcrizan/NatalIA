#!/usr/bin/env bash
# NatalIA environment setup for Linux and macOS — fail fast, reliable, never delete data.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"

export PYTHONUTF8=1
DEV_MODE=true

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dev)
      DEV_MODE=true
      shift
      ;;
    --prod-only)
      DEV_MODE=false
      shift
      ;;
    *)
      shift
      ;;
  esac
done

find_python() {
  for candidate in python3.13 python3.12 python3 python; do
    if command -v "$candidate" >/dev/null 2>&1; then
      if "$candidate" - <<'PY'
import sys
raise SystemExit(0 if sys.version_info >= (3, 12) else 1)
PY
      then
        echo "$candidate"
        return
      fi
    fi
  done
  echo "Error: No compatible Python (>= 3.12) found." >&2
  echo "Please install Python 3.12 or 3.13." >&2
  exit 1
}

PYTHON="$(find_python)"
echo "Selected Python: $(command -v "$PYTHON")"
"$PYTHON" -c "import sys; print('Version:', sys.version.split()[0])"

VENV_PYTHON="$ROOT/.venv/bin/python"
if [[ -x "$VENV_PYTHON" ]]; then
  echo "Found existing virtual environment at .venv"
  if ! "$VENV_PYTHON" - <<'PY'
import sys
raise SystemExit(0 if sys.version_info >= (3, 12) else 1)
PY
  then
    echo "============================================================" >&2
    echo "Error: Existing .venv is incompatible with Python >= 3.12." >&2
    echo "To safely recover, delete the .venv folder and re-run setup:" >&2
    echo "    rm -rf .venv" >&2
    echo "    ./scripts/setup.sh" >&2
    echo "============================================================" >&2
    exit 1
  fi
else
  echo "Creating virtual environment at .venv..."
  "$PYTHON" -m venv "$ROOT/.venv"
fi

LOCK_FILE="requirements.lock"
if [[ "$DEV_MODE" == "true" && -f "$ROOT/requirements-dev.lock" ]]; then
  LOCK_FILE="requirements-dev.lock"
fi

echo "Installing dependencies from $LOCK_FILE..."
"$VENV_PYTHON" -m pip install -r "$ROOT/$LOCK_FILE"

echo "Installing NatalIA package in editable mode..."
"$VENV_PYTHON" -m pip install --no-deps -e "$ROOT"

echo "Verifying core imports..."
"$VENV_PYTHON" -c "import natalia, fastapi, z3, sympy; print('Core imports OK! NatalIA version:', natalia.__version__)"

echo ""
echo "============================================================"
echo " NatalIA setup completed successfully!"
echo " To start the verification workbench, run:"
echo "     ./scripts/run.sh"
echo "============================================================"
echo ""

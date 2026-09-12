#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONUTF8=1
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
  echo "No compatible Python (>= 3.12) found" >&2
  exit 1
}
PYTHON="$(find_python)"
echo "Interpreter: $(command -v "$PYTHON")"
"$PYTHON" -c "import sys; print('Version:', sys.version)"
if [[ -x .venv/bin/python ]]; then
  echo "Found existing virtualenv at .venv"
  .venv/bin/python - <<'PY'
import sys
raise SystemExit(0 if sys.version_info >= (3, 12) else 1)
PY
else
  echo "Creating .venv"
  "$PYTHON" -m venv .venv
fi
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m pip install --no-deps -e .
.venv/bin/python -c "import natalia, fastapi, z3, sympy; print('imports ok', natalia.__version__)"
echo "Setup complete. Run scripts/run.sh"

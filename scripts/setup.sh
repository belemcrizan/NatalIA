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
find_node() {
  if ! command -v node >/dev/null 2>&1; then
    echo "Node.js is required to build the React frontend (20.19+ or 22.12+)." >&2
    exit 1
  fi
  echo "Node: $(node -v)"
  node -e 'const [maj,min]=process.versions.node.split(".").map(Number); if(!((maj===20&&min>=19)||(maj===22&&min>=12)||maj>=23)) process.exit(1)'
}
find_node
echo "Installing frontend dependencies and building React assets"
(
  cd frontend
  if [[ -f package-lock.json ]]; then npm ci; else npm install; fi
  npm run build
)
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
echo "Setup complete."
echo "Start the packaged app with: ./scripts/run.sh"
echo "Then open http://127.0.0.1:8000 (FastAPI serves the React build)."
echo "Optional development UI: npm --prefix frontend run dev (proxies /api to port 8000)."

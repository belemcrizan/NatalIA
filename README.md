# NatalIA

**Evidence-first local workbench for verifying mathematical and physical claims with inspectable guarantees.**

NatalIA provides a local verification environment for physical and mathematical claims with inspectable, end-to-end evidence. The standard user journey is **Describe → Formalize → Review → Verify**, without manual JSON editing; Advanced mode exposes the underlying JSON DSL and SMT-LIB representation. Works completely offline without GPUs, LLM API keys, or cloud accounts.

> **Epistemic Disclaimer**: This version verifies the **declared formalization**, not raw natural-language articles or unparsed LaTeX. **Fast / SMT acceptance is relative to the SMT solver and is not an independent proof certificate.** Proving the formal statement does not guarantee semantic fidelity to the physical system or source document. Content hashes do not authenticate authors; digital signatures (when present) do not prove mathematical truth. Consult the research program in [docs/RESEARCH_SPECIFICATION.md](docs/RESEARCH_SPECIFICATION.md) and the trust boundaries in [docs/TRUST.md](docs/TRUST.md).

---

## Capabilities & Implementation Status

| State | Scope & Components |
| :--- | :--- |
| **Implemented** | React + TypeScript + Vite UI served by FastAPI; local loopback laboratory; DSL v1.0; Fast verification mode (Z3 SMT relative solver + exact rational witness evaluation + boxed intervals); Certified verification mode (independent polynomial identity / sum-of-squares kernel `natalia.kernel`); certificate recheck API; durable SQLite schema v4 jobs with SSE progress; CLI (`natalia run`, `natalia doctor`, `natalia verify`); `distributed` profile with API keys and tenant isolation; on-disk artifact persistence; transactional outbox; test Helm chart; traceability matrix (10/10). |
| **Experimental** | Lean 4 bounded integer positivity fragment (`formal/`, pinned toolchain; product path is `verification_mode=lean`, fail-closed); Docker Compose `distributed` profile (PostgreSQL and NATS companions, **not** bound to API runtime); basic rate-limiting quotas. |
| **Planned** | Google Cloud Platform readiness (Cloud Run + Cloud SQL PostgreSQL + Cloud Storage; see [docs/GCP_READINESS.md](docs/GCP_READINESS.md)); OIDC authentication; durable shared PostgreSQL adapter; OTLP export exercised against a collector. |

**Unauthenticated mode is strictly limited to local loopback (`127.0.0.1`).** `NATALIA_PROFILE=distributed` enforces `X-API-Key` or `Authorization: Bearer`. Target metrics for SLO, operational costs, and >80% auto-formalization accuracy are research goals, not yet empirically measured.

- Canonical Glossary: [docs/GLOSSARY.md](docs/GLOSSARY.md)
- GCP Deployment & Architecture Record: [docs/GCP_READINESS.md](docs/GCP_READINESS.md)
- Trust Boundaries: [docs/TRUST.md](docs/TRUST.md)
- Specification & Research Plan: [docs/RESEARCH_SPECIFICATION.md](docs/RESEARCH_SPECIFICATION.md)
- Traceability Matrix: [docs/TRACEABILITY.md](docs/TRACEABILITY.md)
- System Diagnosis: [docs/DIAGNOSIS.md](docs/DIAGNOSIS.md)
- Gap register: [docs/GAP_REGISTER.md](docs/GAP_REGISTER.md)
- Current release evidence: [docs/RELEASE_EVIDENCE.md](docs/RELEASE_EVIDENCE.md)

---

## Quickstart: Local Execution

### Requirements
- **Python 3.12 or 3.13** (tested and verified on Windows 11 with CPython 3.13.3; 3.12 is the CI baseline).
- **Node.js 20.19+ or 22.12+** only while building the React frontend (`scripts/setup.ps1` / `scripts/setup.sh`). The packaged app does **not** need a Node server at runtime.
- ~1 GB free memory and internet access during initial dependency installation.
- After installation, the application runs entirely locally without contacting external services. FastAPI serves the compiled Vite assets from `natalia/web`.

### Automated Setup & Startup

#### Windows (PowerShell)
```powershell
# Clones repository and sets up virtual environment without deleting existing data
git clone https://github.com/belemcrizan/NatalIA.git
cd NatalIA

# Run setup (installs locked dependencies into .venv)
.\scripts\setup.ps1

# Run system diagnostic checks
.\scripts\doctor.ps1

# Start local server on port 8000
.\scripts\run.ps1
```

#### Linux / macOS (Bash)
```bash
git clone https://github.com/belemcrizan/NatalIA.git
cd NatalIA

chmod +x scripts/setup.sh scripts/run.sh
./scripts/setup.sh
./scripts/run.sh
```

### CLI Invocations
When installed in editable or standard mode, the `natalia` command-line entrypoint is available:

```bash
# Start local server
natalia run --host 127.0.0.1 --port 8000

# Run environment and solver diagnostics
natalia doctor

# Verify a formalization file directly from terminal
natalia verify natalia/examples/01-energy.json

# Check installed version and schema
natalia version
```

### Manual Installation
```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.lock
npm --prefix frontend ci
npm --prefix frontend run build
pip install --no-deps -e .
python -m uvicorn natalia.api:create_app --factory --host 127.0.0.1 --port 8000 --workers 1
```

Do not clone the repository again inside an existing checkout. FastAPI serves `natalia/web` produced by the Vite build. A missing `natalia/web/index.html` fails startup; the retired HTML UI is not used.

Supported runtimes are listed in `runtime_versions.json` (Python 3.12/3.13; Node 20.19+ or 22.12+ for the frontend build only).

Open **http://127.0.0.1:8000**. The English React workspace starts at **Start an investigation**. Guided examples open a scientific narrative; the Claim Builder serializes the DSL. Click **Run verification**. Design notes: [docs/DESIGN.md](docs/DESIGN.md). Feature parity: [docs/FEATURE_PARITY.md](docs/FEATURE_PARITY.md).

Optional frontend development (separate from the normal run command):

```powershell
# terminal 1 — packaged API (serves /api)
.\scripts\run.ps1
# terminal 2 — Vite at http://127.0.0.1:5173, proxy /api → :8000
npm --prefix frontend run dev
```

Use the same hostname (`127.0.0.1` or `localhost`) in the browser and API. Job history survives restarts; interrupted runs are operational failures, not scientific refutations. `Ctrl+C` stops the server.

---

## Docker Compose & Observability

Requires Docker Engine or Docker Desktop with Compose v2. The image is a **multi-stage build**: Node compiles the React app, then a Python image serves the static files. You do not need to prebuild `natalia/web` on the host.

```bash
# Start core application from a clean checkout
docker compose up --build -d
# Access workbench at http://127.0.0.1:8000 after /health/ready returns 200
docker compose logs -f natalia
docker compose down
```

### With Local Observability Stack
```bash
docker compose --profile observability up --build -d
```

| Service | Local Address | Description |
| :--- | :--- | :--- |
| **Workbench** | http://127.0.0.1:8000 | Web UI and REST API |
| **OpenAPI / Swagger** | http://127.0.0.1:8000/docs | Interactive API documentation |
| **Prometheus** | http://127.0.0.1:9090 | Scrapes `/metrics` |
| **Grafana** | http://127.0.0.1:3000 | Pre-configured dashboard: *NatalIA · Local verification* |

Grafana allows anonymous local viewing. For administration, set `GRAFANA_ADMIN_PASSWORD` in `.env` (default: `admin` / `local-change-me`). The named volume `natalia-data` preserves SQLite database and generated artifacts.

---

## Benchmark Examples

The built-in regression suite exercises foundational physical and mathematical verification scenarios:

| Example | Expected Verdict | Epistemic Significance |
| :--- | :--- | :--- |
| **Non-negative kinetic energy** | `ACCEPTED` | SMT relative proof under positive mass and consistent physical dimensions |
| **A failing conjecture ($x^2 \ge x$)** | `REFUTED` | Exact rational counterexample independently re-evaluated and certified |
| **Energy added to momentum** | `INVALID` | Static dimensional mismatch caught before dispatching to solvers |
| **Rational limit at infinity** | `ABSTAIN` | Informative SymPy result; advisory without formal proof certificate |
| **Incomplete deduction** | `ABSTAIN` | Open obligation prevents acceptance |
| **Contradictory assumptions** | `ABSTAIN` | Vacuous truth blocked; unsatisfiable premise check |
| **Division without domain ($x/x = 1$)** | `ABSTAIN` | Singularity at zero is not silently overlooked |
| **Explicitly safe domain ($x \ne 0$)** | `ACCEPTED` | Explicit domain precondition allows proof |
| **Oscillatory limit** | `ABSTAIN` | Outside supported local asymptotic fragment |

### Command-Line API Example
```bash
curl -X POST http://127.0.0.1:8000/api/runs \
  -H "Content-Type: application/json" \
  --data-binary @natalia/examples/02-counterexample.json
```

---

## Verification Architecture & Guarantees

NatalIA maintains a strict separation between **Operational Job Status** and **Scientific Verdict**:

```
Job Lifecycle:       QUEUED ──────► RUNNING ──────► SUCCEEDED / FAILED
                                                        │
Scientific Verdict:                                     ├── ACCEPTED
                                                        ├── REFUTED
                                                        ├── INVALID
                                                        └── ABSTAIN
```

### Epistemic Guarantee Levels
1. **`KERNEL_CHECKED`**: Verified by the independent, deterministic polynomial kernel (`natalia.kernel`). Does not rely on external solver trust.
2. **`SMT_RELATIVE`**: Proven by Z3 relative to the axioms of non-linear real arithmetic (QF_NRA).
3. **`EXACT_WITNESS_CHECKED`**: Refuted with a concrete counterexample verified via exact rational arithmetic ($\mathbb{Q}$).
4. **`ADVISORY`**: Calculated by symbolic CAS (SymPy) or heuristics; informative evidence without formal certificates.

### Dimensional Algebra
All variables define base SI dimensions as a 7-element vector with rational exponents:
$$\mathbf{d} = [M, L, T, I, \Theta, N, J]$$
Dimensional compatibility is verified prior to solver dispatch.

---

## Testing & Quality Assurance

Run the comprehensive local verification suite:

```bash
# 1. Linting & code format check
python -m ruff check .

# 2. Complete unit, integration & contract test suite (109+ tests)
python -m pytest

# 3. Solver regression benchmark (9/9 packaged examples)
python scripts/benchmark.py

# 4. End-to-end full user flow reproduction
python scripts/reproduce_flow.py

# 5. Browser E2E suite (Playwright Chromium)
python scripts/e2e.py
```

---

## Google Cloud Platform (GCP) Readiness

NatalIA is engineered for seamless transition from local research to managed Google Cloud infrastructure. See [docs/GCP_READINESS.md](docs/GCP_READINESS.md) for complete details:
- **Cloud Run**: Serverless, auto-scaling containerized API worker with scale-to-zero cost controls.
- **Cloud SQL (PostgreSQL 16)**: Multi-tenant relational persistence replacing local SQLite.
- **Cloud Storage (GCS)**: Immutable bucket storage for kernel certificates, witness traces, and export bundles.
- **Secret Manager**: Encrypted credential and key management.
- **IAM Least Privilege**: Workload Identity Federation with dedicated service accounts.

The packaged UI is a **React + TypeScript + Vite** build served by FastAPI. There is no fallback to the retired HTML/JavaScript pages. Validation corpus notes remain in [docs/VALIDATION.md](docs/VALIDATION.md).

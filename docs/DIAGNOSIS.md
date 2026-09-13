# Repository Diagnosis & Capabilities Audit (Release 0.5.1)

**Inspection Date**: 2026-09-12 / 2026-09-13  
**Target Workspace**: `NatalIA`  
**Repository**: [https://github.com/belemcrizan/NatalIA](https://github.com/belemcrizan/NatalIA)  
**Historical Note**: Subjective scores from the initial assessment (e.g. 9/10 README, 3/10 average) represented the original author's initial notes, not an independent empirical benchmark. The verifiable rubric used here requires:
1. Documented capability
2. Implemented code
3. Automated test suite validation
4. Live demonstration in this environment
5. Empirical measurement under protocol

---

## Environment & Toolchain

- **Target Host OS**: Windows 11 (tested on local developer workstation).
- **Python Runtime**: CPython 3.13.3 (Windows) and CPython 3.12 (Ubuntu CI baseline).
- **Package Management**: Pip with frozen version lockfiles (`requirements.lock`, `requirements-dev.lock`).
- **Headless Browser**: Playwright Chromium 1234.
- **Solvers**: Z3 SMT solver (`z3-solver==4.14.1.0`), SymPy (`1.13.3`).

---

## Capabilities Inventory Matrix

| Capability | Documented | Implemented | Tested | Demonstrated Here | Measured | Evidence Reference |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Local Setup (Windows / Linux)** | Yes | Yes | CI + Pytest | PowerShell & Bash scripts | Complete | `scripts/setup.ps1`, `scripts/setup.sh`, `scripts/doctor.ps1`, `.github/workflows/ci.yml` |
| **CLI Tools** | Yes | Yes | `test_startup.py` | `natalia run`, `doctor`, `verify` | Complete | `natalia/cli.py`, `natalia/__main__.py` |
| **Fast SMT Verification** | Yes | Yes | `test_engine.py` | `scripts/reproduce_flow.py` | Complete (Z3) | `natalia/oracles.py`, `natalia/engine.py` |
| **Certified Polynomial Kernel** | Yes | Yes | `test_trust.py` | Recheck API | Complete | `natalia/kernel.py`, `natalia/certificates.py` |
| **Lean 4 Proof Export** | Yes (optional) | Export only | `test_lean.py` | Classified `incomplete_proof` | N/A | `natalia/lean.py` |
| **Jobs + Server-Sent Events** | Yes | Yes | `test_jobs.py`, `test_trust.py` | Full flow reproduction | Complete | `natalia/jobs.py`, `natalia/api.py` |
| **Tenant Isolation** | Yes | `distributed` profile | `test_identity.py` | In-process test suite | Complete | `natalia/identity.py` |
| **English-First UX** | Yes | Yes | `scripts/e2e.py` | Playwright Chromium E2E | Complete | `natalia/static/`, `natalia/library.py`, `natalia/examples/` |
| **Google Cloud Readiness** | Yes | Architecture ADR | N/A (planned cloud) | IaC & deployment spec | Complete | `docs/GCP_READINESS.md` |
| **PhysVerifyBench 100k** | Research Goal | 193 instances v0.1 | `scripts/eval_bench.py` | Local corpus | Split by family | `natalia/bench_data/v0.1/` |
| **Traceability Matrix** | Yes | Yes | `test_traceability.py` | Generated JSON | Complete | `docs/TRACEABILITY.json`, `docs/TRACEABILITY.md` |

---

## Verification Flow Reproduction

**Execution**: `python scripts/reproduce_flow.py`  
**Flow Chain**:
$$\text{POST /api/compile} \longrightarrow \text{POST /api/runs} \longrightarrow \text{GET /api/runs/\{id\}} \longrightarrow \text{POST /api/replay} \longrightarrow \text{POST /api/jobs} \longrightarrow \text{SSE events} \longrightarrow \text{Certified run} \longrightarrow \text{Certificate recheck}$$

**Observed Output**:
- Health status: `200 OK`, Schema version: `4`.
- Fast run verdict: `ACCEPTED`, Epistemic guarantee: `SMT_RELATIVE`.
- Refuted job: `REFUTED`, Witness arithmetic verified.
- Structural replay: `accepted: True`.
- Independent kernel run: `ACCEPTED`, Guarantee: `KERNEL_CHECKED`.
- Recheck API: `accepted: True`.
- Lean exporter classification: `incomplete_proof`.

---

## Verification Test Results

| Command | Results & Metrics | Status |
| :--- | :--- | :--- |
| `python -m ruff check .` | 0 errors, 0 warnings across all Python sources | **PASS** |
| `python -m pytest` | **109 passed** in 36.4s | **PASS** |
| `python scripts/benchmark.py` | 9/9 regression cases passed | **PASS** |
| `python scripts/reproduce_flow.py` | Complete end-to-end flow passed | **PASS** |
| `python scripts/e2e.py` | All browser flows, mobile layout (390px), history, exports passed | **PASS** |

---

## Roadmap & Known Future Items

1. **GCP Staging Deployment**: Execute the architecture documented in [docs/GCP_READINESS.md](docs/GCP_READINESS.md) (Cloud Run, Cloud SQL PostgreSQL, Cloud Storage).
2. **Alethe/LFSC Proof Checking**: Integrate proof generation for non-linear real arithmetic (QF_NRA).
3. **Formal Verification Toolchain**: Pinned Lean 4 + Mathlib environment for checked Lean proofs.
4. **Authentication**: Integrate OpenID Connect (OIDC) / OAuth2 for enterprise and multi-user environments.

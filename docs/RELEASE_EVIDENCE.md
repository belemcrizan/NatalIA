# Release evidence (current branch)

This is the current evidence report. Historical counts in [VALIDATION.md](VALIDATION.md) and [DIAGNOSIS.md](DIAGNOSIS.md) stay historical.

## Identity

- Branch: `feat/evidence-based-workbench`
- Base inspected: `feat/react-scientific-workspace` @ `131e120e28babda344734be73fb1a61286e50b24`
- Package version: `0.6.0`
- Runtime policy: [runtime_versions.json](../runtime_versions.json)

## What this revision implements

- Multi-stage Docker build (Node compile, Python serve).
- Manual install documents the React build; missing assets fail closed.
- Build id in Vite HTML/`build.json` and `/health/ready`.
- Occupied-port vs invalid-host distinction; uvicorn workers must stay 1.
- Versioned browser-local drafts.
- Source registry `/api/sources`.
- 15 curated investigations (pilot 12 plus companions); 9 packaged regression examples unchanged in `natalia/examples`.
- Lean mode and pinned `formal/` integer fragment. Layer 1 algebraic lemmas only. No dE/dt theorem.

## What is not claimed

- Not a 9/10 score.
- Not production/cloud validated.
- Not 60 investigations.
- Not Mathlib/PhysLean.
- PostgreSQL/NATS/GCS adapters are not runtime-wired.
- Lean `KERNEL_CHECKED` in this environment requires an installed `lake`/`lean`; otherwise Lean mode abstains.

- Commands run here: `ruff check` pass; `pytest` **120 passed**; frontend vitest **4 passed**; `scripts/benchmark.py` **9/9**.

```powershell
.\scripts\setup.ps1
.\scripts\doctor.ps1
python -m ruff check .
python -m pytest -q
python scripts/benchmark.py
npm --prefix frontend test
```

Linux: `./scripts/setup.sh` then the same Python/npm commands.

Docker (no host frontend prebuild): `docker compose up --build`.

Lean recheck when the toolchain is installed: `cd formal && lake build`.

## Cloud / staging

Blocked: no authorization to provision GCP or expose a public service.

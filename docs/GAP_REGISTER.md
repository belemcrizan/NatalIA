# Gap register (operational)

Compact register for this release. The historical 587-item annex remains in [TRACEABILITY.json](TRACEABILITY.json). Do not treat that matrix as the current gate list.

| ID | Evidence | User impact | Severity | Proposed fix | Regression test | Status | Remaining risk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| G-01 | README manual install omitted the Vite build | Existing users could start API without React assets | High | Document npm ci/build; fail closed if `natalia/web/index.html` missing | `tests/test_api.py` ready/frontend; doctor | Closed in this branch | Users who skip docs still need the error message |
| G-02 | Dockerfile copied host `natalia/web` | Clean checkout Docker build could miss the UI | High | Multi-stage Node→Python image | `tests/test_release.py::test_dockerfile_is_multistage`; CI `container` | Closed in code; CI must still run | ECR/Node image pull failures |
| G-03 | Browser drafts omitted | Refresh lost in-progress claims | Medium | `natalia.drafts.v1` localStorage, labeled browser-local | `frontend/src/lib/drafts.test.ts` | Closed | Not server-backed; no tenant isolation by design |
| G-04 | History run vs job IDs | Confusion if IDs diverged | Medium | Confirmed same UUID space (`JobManager` / `GET /api/runs/{id}` uses job id) | existing job/run tests | Confirmed | Keep using one id |
| G-05 | Lean export used `sorry` | Could be misread as a certificate | High | Pinned `formal/` fragment; `verification_mode=lean` fail-closed | `tests/test_release.py` | Partial | Live `lake build` not run unless Lean is installed |
| G-06 | Root `examples/01-energy.json` vs `natalia/examples` | Container smoke could POST a divergent payload | Medium | Align root smoke file with English submission | `test_root_smoke_example_is_a_submission_not_a_wrapper` | Closed for 01-energy | Other root examples may still differ |
| G-07 | PostgreSQL/NATS Compose companions not bound | Cloud/shared persistence not real | High (cloud) | Keep labeled blocked | — | Blocked | No staging authority |
| G-08 | Investigation library short of 60 | Incomplete teaching corpus | Medium | 15 curated investigations with sources; 9 regression JSON | `test_investigations.py` | Partial | Scaling to 60 still open |
| G-09 | OTLP / collector | Observability profile Prometheus only | Low (local) | Optional; base app must not require collector | — | Blocked | Spans not verified at a collector |
| G-10 | DIAGNOSIS.md pytest 109 / missing `test_identity.py` | Stale validation prose | Low | Point current counts to CI + this register; do not rewrite historical annex counts | — | Documented | Historical docs remain historical |

Current milestone after this PR: **A largely done locally**, **B pilot investigations delivered (15, not 60)**, **C Lean path implemented but toolchain-dependent**, **D–F blocked or partial**.

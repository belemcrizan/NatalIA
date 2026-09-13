# Feature parity — legacy UI to React workspace

| Previous flow | React route | Backend |
| --- | --- | --- |
| Home / start investigation | `/` | `/api/investigations`, `/api/runs` |
| Guided example library + filters | `/library` | `/api/investigations` |
| Investigation narrative + run | `/investigate/:id` | `/api/investigations/:id`, `POST /api/jobs`, SSE |
| Claim builder guided wizard | `/builder` | `/api/examples`, `/api/compile`, `POST /api/jobs` |
| Advanced JSON DSL | `/builder` Advanced DSL | same payload |
| Result, export, recheck, revise | result panel / `/history/:id` | `/api/certificates/recheck`, artifacts |
| History search, pagination, compare, import preview | `/history` | `/api/runs`, `/api/jobs`, `/api/import` |
| Open / replay run | `/history/:id` | `GET /api/jobs/:id`, `POST /api/replay` |
| Cancel in-flight job | Claim builder Cancel | `POST /api/jobs/:id/cancel` |
| Benchmark manifest | `/benchmark` | `/api/benchmark/manifest` |
| Trust contract | `/trust` | static + `/api/capabilities` |
| System health / stats | `/diagnostics` | `/api/system`, `/metrics` |
| Capabilities / version | Diagnostics + About text | `/api/capabilities`, `__APP_VERSION__` |
| Onboarding dialog | Home CTAs | none |
| Draft localStorage | `/builder` (banner) | browser-only versioned drafts (`natalia.drafts.v1`); not server history |

Secondary surfaces keep working: catalog endpoints remain on the API even if the library now prefers investigations.

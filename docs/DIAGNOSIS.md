# Diagnóstico do repositório (evolução 0.5)

Inspeção em 2026-09-12 sobre o código do workspace `NatalIA-1`, remoto declarado `https://github.com/belemcrizan/NatalIA`. As notas 9/10 (README) e 3/10 (média do anexo) são **opinião do texto original**, não resultado de auditoria independente. Rubrica verificável antes de uso público: (1) capacidade documentada, (2) implementada, (3) testada, (4) demonstrada neste ambiente, (5) medida com protocolo. Um item só avança de nível com evidência.

## Ambiente

- OS alvo desta sessão: Windows (workspace do responsável).
- Python declarado pelo projeto: `requires-python >= 3.12`; CI: 3.12 (Ubuntu, E2E) e 3.13 (Ubuntu e Windows).
- Interpretador efetivo: registrado após a execução dos comandos abaixo.

## Inventário por capacidade

| Capacidade | Documentada | Implementada | Testada | Demonstrada aqui | Medida | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| Instalação local Windows/Linux | sim | sim | CI + scripts | comandos desta sessão | n/a | `scripts/setup.ps1`, `scripts/setup.sh`, `.github/workflows/ci.yml` |
| Fluxo Fast SMT | sim | sim | `tests/test_engine.py` | `scripts/reproduce_flow.py` | não (sem p95) | `natalia/oracles.py`, `natalia/engine.py` |
| Certified polinomial | sim | sim | `tests/test_trust.py` | recheck API | não (FPR) | `natalia/kernel.py`, `natalia/certificates.py` |
| Lean kernel certificate | sim como opcional | exportação apenas | `tests/test_lean.py` | classificação `incomplete_proof` | n/a | `natalia/lean.py`; `formal/` sem lakefile |
| Jobs + SSE | sim | sim | `tests/test_jobs.py`, `test_trust.py` | reproduce_flow | não | `natalia/jobs.py`, `natalia/api.py` |
| Isolamento tenant | sim | perfil `distributed` | `test_two_tenants_cannot_read_each_other` | testes | não em prod | `natalia/identity.py` |
| Postgres store | README como planejado | Compose companheiro | config compose | não usado pela API | não | `compose.yaml` |
| NATS consumidor | planejado | não | não | não | não | ADR em `docs/DECISIONS.md` |
| OTLP | README negativo | spans locais | parcial | não OTLP | não | `natalia/telemetry.py` |
| Autoformalização LLM | spec | não | não | não | não | `docs/RESEARCH_SPECIFICATION.md` |
| PhysVerifyBench 100k | meta | 193 instâncias v0.1 | `scripts/eval_bench.py` | corpus local | não FPR | `natalia/bench_data/v0.1/` |
| UX guiada | sim | HTML/JS | `scripts/e2e.py` no CI Ubuntu | E2E desta sessão se Playwright existir | não usabilidade humana | `natalia/static/` |
| Licença raiz | anexo P2 | não | n/a | decisão aberta | n/a | sem `LICENSE` na raiz |
| Matriz de requisitos | preâmbulo | sim | `tests/test_traceability.py` | gerada | n/a | `docs/TRACEABILITY.json` |

## Fluxo reproduzido

Script: `python scripts/reproduce_flow.py`

Cadeia: `POST /api/compile` → `POST /api/runs` → `GET /api/runs/{id}` → `POST /api/replay` → `POST /api/jobs` → `GET /api/jobs/{id}/events` → `POST /api/runs` (certified) → `POST /api/certificates/recheck`.

## Comandos desta sessão

Ambiente: Windows 11, CPython 3.13.3, venv `.venv`.

| Comando | Resultado |
| --- | --- |
| `python -m ruff check .` | All checks passed |
| `python -m pytest -q` | **103 passed** (baseline 0.4: 95) em 37.59s |
| `python scripts/reproduce_flow.py` | health ready schema 4; compile ok; Fast ACCEPTED SMT_RELATIVE; job REFUTED; replay accepted; Certified ACCEPTED KERNEL_CHECKED; recheck true; lean_class incomplete_proof |
| `python scripts/benchmark.py` | 9/9 casos locais |
| `scripts/build_traceability.py` (via testes) | 587 registros; anexo SHA-256 `520ee5972fc77692…` |

Playwright E2E, Docker e Helm **não** foram reexecutados nesta sessão. Grafana não foi aberto.

Cleanup do SQLite temporário no Windows pode falhar com arquivo em uso; o script usa `ignore_cleanup_errors=True` após o fluxo ter sido impresso.

## Rubrica para as notas do anexo

Não republicar “README 9/10, código 6/10, ciência 2/10”. Em vez disso, para cada pilar dos oito do resumo, publicar: definição, evidência, o que falta, e se o gate A–F passou. Esta fatia não fecha os oito pilares.

## Estados desta entrega

- **Concluído e validado (testes automatizados):** kernel polinomial no fragmento; recusa de certificado Lean com `sorry`/comentários; isolamento de tenant em processo; matriz gerada a partir do anexo; corpus 9 exemplos.
- **Implementado sem validação suficiente:** SSE em produção de carga; Helm; Compose observability; CoC; templates GitHub; position paper (rascunho).
- **Planejado:** Etapas C–F, Alethe, Postgres store, OIDC, OCR, LLM.
- **Bloqueado:** auditorias pagas, grants, parcerias nomeadas, submissão de papers, escolha de licença.

## Lacunas bloqueadoras restantes (P0 de código)

- Store continua SQLite.
- Sem checker Alethe/LFSC exercitado no fragmento QF_NRA.
- Sem Mathlib pinado.
- Frontend sem WCAG auditado nem i18n completo.
- Sem autenticação OIDC.

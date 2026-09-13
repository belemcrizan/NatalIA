# Validação da evolução 0.5

Ambiente: **Windows 11**, **Python 3.13.3**, venv do repositório.

| Verificação | Resultado observado |
| --- | --- |
| Preservação do anexo | Marcadores BEGIN/END presentes; SHA-256 registrado na matriz |
| Matriz | 587 registros em `docs/TRACEABILITY.json` |
| Ruff | Sem erros |
| pytest | **103 aprovados** |
| Fluxo vertical | `scripts/reproduce_flow.py`: Fast SMT_RELATIVE, Certified KERNEL_CHECKED, Lean `incomplete_proof` ≠ REFUTED |
| Corpus 9/9 | Aprovado |
| Lean 4 toolchain | Não usado como certificado |
| Docker / Grafana / Helm install | Não exercitados nesta sessão |

# Validação da evolução 0.4


Ambiente: **Windows 11**, **Python 3.13.3**.

| Verificação | Resultado observado |
| --- | --- |
| Ruff | Sem erros |
| Testes Python | **95 aprovados** (baseline 0.3: 81) |
| Corpus 9/9 | Aprovado via `scripts/benchmark.py` |
| PhysVerifyBench quick (1/família) | 25/25 no rótulo de sistema; 0 aceites incorretos nesta amostra |
| Lean 4 | Ausente; exportação não é KERNEL_CHECKED |
| Docker / Grafana / Helm install | Não exercitados nesta máquina além dos arquivos adicionados |
| OTLP | Não implementado; spans continuam locais |
| NATS/Postgres como store | Não usados pela API |

Pendências: toolchain Lean+Mathlib, store PostgreSQL, consumidor NATS, OIDC, E2E Playwright desta sessão se Chromium não estiver no PATH.


# Validação da evolução 0.3

Ambiente local: **Windows 11**, **Python 3.13**, virtualenv no caminho com espaços e acento.

| Verificação | Resultado observado |
| --- | --- |
| Baseline 0.2 | 71 testes Python aprovados antes das mudanças |
| Ruff | Sem erros |
| Testes Python 0.3 | **81 aprovados** |
| Biblioteca didática | 34 casos; cada um conferido por `verify` contra o veredito esperado |
| PhysVerifyBench v0.1 | **193/193** alinhados ao rótulo de sistema; 84 casos falsos/mal-tipados sem aceite incorreto nesta amostra |
| Corpus de regressão 9/9 | Aprovado via `scripts/benchmark.py` |
| Meta 200 instâncias | Não atingida de propósito: 193 templates validados, sem enchimento |
| Lean 4 | Ausente; reportado como indisponível |
| Grafana / Docker | Não reexecutados nesta máquina |
| Usabilidade com pessoas | Não realizada; E2E automatizado ≠ teste com participantes |
| Navegador E2E | A executar no CI Ubuntu 3.12; nesta sessão o conjunto Playwright pode ser corrido à parte |

Pendências: Lean real, intervalos em domínio não-caixa, tradução assistida, holdout custodiado, 7 instâncias a menos que a meta 200.

# Validação da evolução 0.2

Ambiente local: **Windows 11**, **Python 3.13.3**, virtualenv no caminho do repositório (espaços e acento em “Área de Trabalho”).

| Verificação | Resultado observado |
| --- | --- |
| Instalação lockfile em 3.13.3 | Dependências, `z3` e `sympy` importaram |
| Ruff | Sem erros após correção de imports |
| Testes Python | **71 aprovados** (baseline anterior: 62) |
| Corpus sintético via pytest | 9/9 vereditos |
| Migração SQLite v1 → v2 | Aprovado |
| Backup e restauração | Aprovado (scripts com `__main__`) |
| Idempotência e conflito | Aprovado |
| Reinício com job `running` | Classificado `failed` / `interrupted_by_restart` |
| Cancelamento de worker | Aprovado (processo spawn + `cancel_check`) |
| Replay com hash adulterado | Rejeitado |
| Navegador E2E | Executado se Playwright/Chromium disponível neste ambiente; o CI Ubuntu 3.12 permanece a fonte do E2E |
| Docker / Grafana | Não executados nesta máquina |
| Cloud | Não provisionada |

Os testes novos cobrem jobs, migração, caminhos com acento, contrato de evidência e spans em erro de compilação. Não medem acurácia científica.

## Pendências conscientes

- Playwright E2E no job Windows do CI (não habilitado).
- Fila entre processos / leases distribuídos.
- OpenTelemetry/OTLP.
- Lean e aritmética intervalar (continuam `not implemented`).
- Tradução por LLM (fluxo manual permanece o único caminho).

## Baseline 0.1 (12/09/2026)

A primeira entrega registrou 62 testes Python no Linux / CPython 3.12.14, corpus 9/9 e E2E de navegador. Esta evolução preserva esses contratos síncronos (`POST /api/runs` → 201) e acrescenta jobs, UI guiada e migração.

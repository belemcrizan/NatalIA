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

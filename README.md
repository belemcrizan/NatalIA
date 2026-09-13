# NatalIA

**Laboratório local de verificação de afirmações matemáticas e físicas, com evidências inspecionáveis.**

Laboratório local de verificação de afirmações matemáticas e físicas, com evidências inspecionáveis. A jornada padrão é **descrever → formalizar → revisar → executar**, sem editar JSON; o modo avançado expõe a DSL. Funciona sem GPU, chave de LLM ou conta cloud.

> Esta versão verifica a **formalização declarada**, não um artigo ou LaTeX livre. **Aceite Fast / SMT não é certificado independente.** Provar a formalização não garante fidelidade ao documento. Hash não autentica origem; assinatura (quando existir) não prova verdade matemática. O programa de pesquisa está em [docs/RESEARCH_SPECIFICATION.md](docs/RESEARCH_SPECIFICATION.md); o contrato de confiança está em [docs/TRUST.md](docs/TRUST.md).

## O que está implementado, experimental ou planejado

| Estado | Conteúdo |
| --- | --- |
| Implementado | Laboratório local loopback; DSL 1.0; Fast (SMT + testemunha exata + intervalos em caixa); Certified no fragmento polinomial `natalia.kernel`; recheck; jobs duráveis; schema SQLite 4; SSE; perfil `distributed` com API keys e isolamento de tenant; artefatos em disco; outbox transacional; Helm de teste; matriz de rastreabilidade do anexo 10/10 |
| Experimental | Exportação Lean com `sorry` explícito e classificação de falha (não é certificado); Compose `distributed` (Postgres/NATS de companhia, não usados pela API ainda); quotas simples |
| Planejado | OIDC, NATS consumidor, PostgreSQL como store, Mathlib pinado, Alethe/LFSC, ingestão de PDF/OCR, autoformalização com revisão, OTLP, sandbox reforçada, leaderboard |

**Modo sem autenticação é exclusivo do uso local em loopback.** `NATALIA_PROFILE=distributed` exige `X-API-Key` ou `Authorization: Bearer`. Metas de SLO, custo e autoformalização >80% **não foram medidas** e permanecem metas.

Programa de rastreabilidade: [docs/TRACEABILITY.md](docs/TRACEABILITY.md). Diagnóstico desta fatia: [docs/DIAGNOSIS.md](docs/DIAGNOSIS.md). Anexo original: [docs/annex/ORIGINAL_CHECKLIST.md](docs/annex/ORIGINAL_CHECKLIST.md). Fast vs Certified: [docs/TRUST.md](docs/TRUST.md). Auditoria: [docs/AUDIT.md](docs/AUDIT.md).

## Executar localmente

Requisitos: **Python 3.12 ou 3.13**, **Node.js 20.19+ ou 22.12+** (apenas para construir o frontend), aproximadamente 1 GB de memória disponível e internet para instalar dependências. Depois da instalação, a aplicação empacotada não consulta serviços externos e **não precisa de um servidor Node**. O schema `/openapi.json` permanece acessível offline. A página Swagger (`/docs`) usa os recursos externos padrão do FastAPI.

```powershell
# Windows (detecta o interpretador, cria/reutiliza .venv, não apaga dados)
git clone https://github.com/belemcrizan/NatalIA.git
cd NatalIA
.\scripts\setup.ps1
.\scripts\run.ps1
```

```bash
# Linux / macOS
git clone https://github.com/belemcrizan/NatalIA.git
cd NatalIA
chmod +x scripts/setup.sh scripts/run.sh
./scripts/setup.sh
./scripts/run.sh
```

Diagnóstico: `.\scripts\doctor.ps1`. Os scripts usam o Python da virtualenv diretamente; não é necessário ativá-la. Pare o servidor com Ctrl+C. Abra **http://127.0.0.1:8000**.

Instalação manual equivalente:

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows: .venv\Scripts\python.exe -m pip ...
python -m pip install -r requirements.lock
python -m pip install --no-deps -e .
python -m uvicorn natalia.api:create_app --factory --host 127.0.0.1 --port 8000 --workers 1
```

Abra **http://127.0.0.1:8000**. A interface React em inglês começa em **Start an investigation**. Cada exemplo guiado abre uma narrativa científica; o Claim Builder gera a DSL. Clique em **Run verification**. O racional de design está em [docs/DESIGN.md](docs/DESIGN.md); paridade de fluxos em [docs/FEATURE_PARITY.md](docs/FEATURE_PARITY.md).

Modo de desenvolvimento (opcional, separado do comando normal):

```bash
# terminal 1 — API
.\scripts\run.ps1
# terminal 2 — Vite em http://127.0.0.1:5173, proxy /api → :8000
npm --prefix frontend run dev
```

Use o mesmo hostname (`127.0.0.1` ou `localhost`) no browser e na API. O histórico e o estado dos jobs sobrevivem a reinícios; execuções interrompidas aparecem como falha operacional, não como refutação. `Ctrl+C` encerra o servidor.

Os lockfiles fixam as versões transitivas testadas; são locks de versões, sem hashes de distribuição. `pyproject.toml` declara as dependências diretas.

Decisões desta evolução: [docs/DECISIONS.md](docs/DECISIONS.md).

### Docker Compose

Requer Docker Engine/Desktop com Compose v2:

```bash
docker compose up --build -d
# Mesma interface: http://127.0.0.1:8000
docker compose logs -f natalia
docker compose down
```

Com monitoramento adicional:

```bash
docker compose --profile observability up --build -d
```

Companheiros de integração (não usados pela API ainda):

```bash
docker compose --profile distributed config --quiet
```

O perfil `distributed` publica Postgres e NATS em loopback para integração futura. A API **ainda persiste em SQLite**. Não é um cluster de produção.

Helm de teste: `deploy/helm/natalia` (SQLite em PVC).

| Serviço | Endereço local |
| --- | --- |
| Laboratório | http://127.0.0.1:8000 |
| OpenAPI / Swagger | http://127.0.0.1:8000/docs |
| Prometheus | http://127.0.0.1:9090 |
| Grafana, dashboard “NatalIA · Local verification” | http://127.0.0.1:3000 |

Grafana permite visualização anônima local. Para administração, configure `GRAFANA_ADMIN_PASSWORD` em `.env`; o fallback de desenvolvimento é `admin` / `local-change-me`. A aplicação Python lê variáveis do ambiente, não carrega `.env` automaticamente; Compose carrega o arquivo para interpolação.

O volume `natalia-data` preserva o histórico. **`docker compose down -v` apaga os volumes**; o CI usa isso apenas em seu ambiente descartável. As portas são publicadas em loopback, sem exposição à rede. O contêiner usa usuário sem privilégios, filesystem somente leitura e limites de CPU/memória/processos.

## O que experimentar

| Exemplo | Resultado esperado | O que demonstra |
| --- | --- | --- |
| Energia cinética não negativa | `ACCEPTED` | Prova SMT relativa com massa positiva e dimensões físicas |
| `x**2 >= x` para reais | `REFUTED` | Contraexemplo racional conferido independentemente |
| Energia somada ao momento | `INVALID` | Erro dimensional antes de despachar solver |
| Limite racional em infinito | `ABSTAIN` | Resultado SymPy informativo, sem certificado |
| Dedução incompleta | `ABSTAIN` | Uma obrigação aberta impede aceite |
| Premissas contraditórias | `ABSTAIN` | Bloqueio de aceite por vacuidade |
| `x/x == 1` sem domínio | `ABSTAIN` | Singularidade em zero não é ignorada |
| `x/x == 1`, com `x != 0` | `ACCEPTED` | Domínio explicitamente válido |
| Limite oscilatório | `ABSTAIN` | Fora do fragmento assintótico local |

É possível editar todo o JSON. As dimensões seguem **[M, L, T, I, Θ, N, J]**, com expoentes racionais em strings. Consulte a [DSL e contrato da API](docs/DSL.md).

Exemplo por terminal:

```bash
curl -H 'Content-Type: application/json' \
  --data-binary @examples/02-counterexample.json \
  http://127.0.0.1:8000/api/runs
```

No PowerShell, use `curl.exe` ou `Invoke-RestMethod`. Em `ACCEPTED`, o JSON inclui o problema SMT-LIB cuja negação foi considerada insatisfatível. Em `REFUTED`, inclui a atribuição exata e a relação violada. Todos os resultados carregam hash da entrada, versões, tempos e IDs de correlação.

## Testar

```bash
python -m pip install -r requirements-dev.lock
python -m pip install --no-deps -e .
python -m ruff check .
python -m pytest -q
python scripts/benchmark.py
python scripts/eval_bench.py --build
python scripts/eval_bench.py
python -m playwright install chromium
python scripts/e2e.py
```

No Linux, se faltarem bibliotecas do navegador, instale-as com o mecanismo recomendado pelo Playwright (`playwright install --with-deps chromium`, quando houver permissões). Também é possível apontar `NATALIA_CHROMIUM_PATH` para um Chromium já instalado.

O teste de navegador inicia uma API isolada em porta livre e usa banco temporário. Exercita os nove exemplos, histórico, exportação, JSON inválido, métricas, texto hostil e layout móvel; grava evidências em `artifacts/`. O CI executa testes Python, navegador e um job separado de build e smoke test do contêiner.

O corpus incluído tem **nove casos de regressão na API `/api/examples`**, **34 casos didáticos** em `/api/catalog` e **193 instâncias** no PhysVerifyBench v0.1 (público, split por família). Não estima FPR populacional, ECE ou validade científica geral. Consulte [validação da entrega](docs/VALIDATION.md).

## Componentes e operação

- **Frontend:** React + TypeScript + Vite, servido como assets estáticos pelo FastAPI; TanStack Query; Claim Builder com React Hook Form/Zod; KaTeX e Recharts locais.
- **API:** FastAPI, jobs persistentes (`queued` → `running` → terminal), idempotência, cancelamento, replay estrutural de evidências.
- **Compilador:** AST permitida, álgebra dimensional exata em ℚ⁷ e limites de complexidade.
- **Persistência:** SQLite WAL, schema 4 (migração v1→v4: tenants, chaves, artefatos, outbox).
- **Verificação:** Fast = Z3 relativo + testemunhas racionais + intervalos em caixa + SymPy consultivo. Certified = kernel polinomial independente; SMT não promove aceite.
- **Multi-tenant:** opcional; identidade vem da API key, nunca de `tenant_id` no JSON.
- **Observabilidade:** logs JSON, Prometheus, spans locais — **não OTLP**.

O modo local permanece utilizável sem serviços pagos. Execute somente em loopback sem autenticação. Veja [runbook](docs/RUNBOOK.md).

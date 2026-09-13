# NatalIA

**Laboratório local de verificação de afirmações matemáticas e físicas, com evidências inspecionáveis.**

Laboratório local de verificação de afirmações matemáticas e físicas, com evidências inspecionáveis. A jornada padrão é **descrever → formalizar → revisar → executar**, sem editar JSON; o modo avançado expõe a DSL. Funciona sem GPU, chave de LLM ou conta cloud.

> Esta versão verifica a **formalização declarada**, não um artigo ou LaTeX livre. Um aceite é relativo à codificação SMT e às premissas informadas; não é um certificado Lean. O programa neuro-simbólico completo está descrito no [roadmap](docs/ROADMAP.md). A [especificação original fornecida](docs/RESEARCH_SPECIFICATION.md) está preservada como proposta de pesquisa; os limites implementados estão na [arquitetura](docs/ARCHITECTURE.md).

## Executar localmente

Requisitos: **Python 3.12 ou 3.13** (3.13.3 foi exercitado no Windows; 3.12 permanece a baseline do E2E no CI), aproximadamente 1 GB de memória disponível e internet para instalar dependências. Depois da instalação, a aplicação não consulta serviços externos. O frontend principal não usa CDN nem requer Node. A página opcional Swagger (`/docs`) usa os recursos externos padrão do FastAPI; o schema `/openapi.json` permanece acessível offline.

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

Abra **http://127.0.0.1:8000**. No modo guiado, a navegação começa em **Início** (Nova investigação / Explorar exemplos). Escolha um caso, revise o resumo e clique em **Verificar hipótese**. O histórico e o estado dos jobs sobrevivem a reinícios; execuções interrompidas aparecem como falha operacional, não como refutação. `Ctrl+C` encerra o servidor.

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

- **Frontend:** HTML/CSS/JavaScript sem build; modo guiado e avançado; rascunhos no `localStorage` do navegador.
- **API:** FastAPI, jobs persistentes (`queued` → `running` → terminal), idempotência, cancelamento, replay estrutural de evidências.
- **Compilador:** AST permitida, álgebra dimensional exata em ℚ⁷ e limites de complexidade.
- **Verificação:** Z3 sobre reais, testemunhas racionais, enclosure intervalar exato quando há caixa, SymPy consultivo. Lean 4 é opcional e, sem o executável, permanece indisponível.
- **Execução:** jobs persistentes; fila com claim atômico; `POST /api/runs` síncrono; `POST /api/jobs` assíncrono. Semântica at-least-once.
- **Persistência:** SQLite WAL, schema 3 (migração v1→v2→v3).
- **Observabilidade:** logs JSON, métricas Prometheus (incluindo estados de job), spans também em erros de compilação.

A interface de observabilidade mostra métricas históricas do SQLite. Os contadores Prometheus pertencem ao processo e reiniciam junto com a API. Spans são rastros locais de aplicação, **não uma implementação OTLP/OpenTelemetry**.

Não há autenticação nesta etapa: execute somente no computador de teste. A implantação cloud depende dos critérios do [roadmap](docs/ROADMAP.md), sem escolher provedor antecipadamente. Veja [arquitetura](docs/ARCHITECTURE.md) e [runbook](docs/RUNBOOK.md).

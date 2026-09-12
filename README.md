# NatalIA

**Laboratório local de verificação de afirmações matemáticas e físicas, com evidências inspecionáveis.**

Primeira entrega end-to-end: interface em português → DSL explícita → checagem dimensional → Z3 / SymPy → veredito e evidências → histórico SQLite → métricas e rastros. Funciona sem GPU, chave de LLM ou conta cloud.

> Esta versão verifica a **formalização declarada**, não um artigo ou LaTeX livre. Um aceite é relativo à codificação SMT e às premissas informadas; não é um certificado Lean. O programa neuro-simbólico completo está descrito no [roadmap](docs/ROADMAP.md). A [especificação original fornecida](docs/RESEARCH_SPECIFICATION.md) está preservada como proposta de pesquisa; os limites implementados estão na [arquitetura](docs/ARCHITECTURE.md).

## Executar localmente

Requisitos: **Python 3.12**, aproximadamente 1 GB de memória disponível e internet para instalar dependências. Depois da instalação, a aplicação não consulta serviços externos. O frontend principal não usa CDN nem requer Node. A página opcional Swagger (`/docs`) usa os recursos externos padrão do FastAPI; o schema `/openapi.json` permanece acessível offline.

```bash
git clone https://github.com/belemcrizan/NatalIA.git
cd NatalIA
# Enquanto o PR estiver aberto, use a branch da primeira entrega:
git switch feat/local-verification-workbench
python -m venv .venv
```

Ative o ambiente:

```bash
# Linux / macOS
source .venv/bin/activate
```

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Instale e execute:

```bash
python -m pip install -r requirements.lock
python -m pip install --no-deps -e .
python -m uvicorn natalia.api:create_app --factory --host 127.0.0.1 --port 8000 --workers 1
```

Abra **http://127.0.0.1:8000**. Selecione um experimento, clique em **Verificar hipótese**, inspecione as obrigações e exporte o JSON. O histórico continua disponível após reiniciar. `Ctrl+C` encerra o servidor.

Os lockfiles fixam as versões transitivas testadas; são locks de versões, sem hashes de distribuição. `pyproject.toml` declara as dependências diretas. Use Python 3.12 para reproduzir a entrega.

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
python -m playwright install chromium
python scripts/e2e.py
```

No Linux, se faltarem bibliotecas do navegador, instale-as com o mecanismo recomendado pelo Playwright (`playwright install --with-deps chromium`, quando houver permissões). Também é possível apontar `NATALIA_CHROMIUM_PATH` para um Chromium já instalado.

O teste de navegador inicia uma API isolada em porta livre e usa banco temporário. Exercita os nove exemplos, histórico, exportação, JSON inválido, métricas, texto hostil e layout móvel; grava evidências em `artifacts/`. O CI executa testes Python, navegador e um job separado de build e smoke test do contêiner.

O corpus incluído tem **nove casos sintéticos de regressão**. Não equivale aos 5.000 itens de PhysVerifyBench propostos na especificação, e não estima FPR, ECE ou validade científica geral. Consulte [validação da entrega](docs/VALIDATION.md).

## Componentes e operação

- **Frontend:** HTML/CSS/JavaScript sem build, responsivo, servido pela API na mesma origem.
- **API:** FastAPI, esquema Pydantic estrito, erros de validação e endpoints de saúde.
- **Compilador:** AST permitida, álgebra dimensional exata em ℚ⁷ e limites de complexidade.
- **Verificação:** Z3 sobre reais, checagem independente de testemunhas racionais; SymPy como consultor assintótico.
- **Execução:** processo descartável por submissão, orçamento de parede e no máximo dois workers por padrão. Sem fila: saturação retorna HTTP 429.
- **Persistência:** SQLite com WAL, versão de schema, histórico paginado e backup consistente.
- **Observabilidade:** logs JSON, métricas Prometheus, spans locais persistidos e dashboard Grafana opcional.

A interface de observabilidade mostra métricas históricas do SQLite. Os contadores Prometheus pertencem ao processo e reiniciam junto com a API. Spans são rastros locais de aplicação, **não uma implementação OTLP/OpenTelemetry**.

Não há autenticação nesta etapa: execute somente no computador de teste. A implantação cloud depende dos critérios do [roadmap](docs/ROADMAP.md), sem escolher provedor antecipadamente. Veja [arquitetura](docs/ARCHITECTURE.md) e [runbook](docs/RUNBOOK.md).

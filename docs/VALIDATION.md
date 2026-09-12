# Validação da primeira entrega

Executada no ambiente de desenvolvimento em **12/09/2026**, Linux / Python 3.12.14.

| Verificação | Resultado observado |
| --- | --- |
| Ruff | Sem erros |
| Sintaxe JavaScript (`node --check`) | Aprovada |
| Testes Python | **62 aprovados** |
| Corpus sintético, processos reais | **9/9 vereditos esperados** |
| Navegador end-to-end | **Aprovado**, incluindo os nove experimentos |
| Histórico após reload e nova conexão SQLite | Aprovado |
| Exportação JSON | Aprovada e conteúdo conferido |
| Submissão de JSON inválido | Erro visível, sem execução |
| Texto hostil na interface | Renderizado como texto, sem execução de HTML |
| Viewport móvel 390 × 844 | Sem overflow horizontal; interface inspecionada |
| Viewport desktop 1440 × 1050 | Interface inspecionada |
| Docker / Compose / Grafana em execução | **Não executados neste ambiente; Docker indisponível** |
| Cloud | Não provisionada nesta etapa |

Os testes Python incluem parsing restrito, limites da AST, dimensões fracionárias, inconsistência dimensional, premissas contraditórias, divisões indefinidas, evidência racional independente, testemunhas algébricas não suportadas, falha de worker, timeout com encerramento, HTTP 429 sob concorrência, readiness, correlação de logs sem conteúdo da pesquisa, persistência e limites HTTP.

O script E2E inicia uma API real em porta livre, executa os solvers em processos descartáveis e usa SQLite temporário. Não substitui respostas do backend por mocks. Os testes HTTP unitários usam o motor real no mesmo processo para agilidade; a suíte de worker e o E2E verificam separadamente a fronteira de processo.

## Navegador usado nesta validação

O download padrão do Chromium da versão de Playwright instalada falhou na CDN. O teste foi concluído usando **Chromium Headless Shell 134.0.6998.35**, obtido pela distribuição Playwright, com o runner Playwright 1.62.0 e `NATALIA_CHROMIUM_PATH` configurado. O CI usa `playwright install --with-deps chromium` para instalar o navegador correspondente ao lockfile; a execução local com o Chromium padrão dessa versão não foi confirmada.

Evidências reproduzíveis geradas em `artifacts/`: `laboratory-desktop.png`, `counterexample-desktop.png`, `observability-desktop.png`, `laboratory-mobile.png`, `export.json` e `e2e-server.log`. Não são incluídas no versionamento; o CI as publica como artefato de teste.

Duas advertências de depreciação aparecem no TestClient de Starlette/AnyIO com HTTPX. Não houve falhas de teste. Elas ficam visíveis para manutenção das dependências, sem filtros que ocultem warnings.

## Como interpretar

Os testes demonstram o comportamento da baseline dentro dos casos exercitados. Não constituem uma prova de correção do compilador ou do Z3, nem avaliação independente de fidelidade da formalização. Nenhum FPR, ECE, confiança calibrada ou ganho de RL foi medido. O corpus é de regressão, não o benchmark de pesquisa proposto.

O workflow tem um job dedicado para build do contêiner, healthcheck e submissão real. Sua presença no repositório **não equivale a uma execução bem-sucedida**; consulte os checks do PR para o estado remoto.

# Decisões da evolução 0.2

## Jobs no mesmo processo

Fila durável entre máquinas exigiria um executor separado. Nesta rodada os jobs são gravados no SQLite **antes** do cálculo, o estado sobrevive a reinício (como falha operacional, sem veredito científico) e o cancelamento encerra o processo descartável. A entrega continua *at-least-once* para a persistência do registro; não há exatamente-uma-vez.

`POST /api/runs` permanece síncrono (201) para clientes existentes. `POST /api/jobs` devolve 202 e a UI consulta o progresso.

## SQLite e schema 2

PostgreSQL não foi introduzido: o produto é local, um usuário, um processo. A tabela `jobs` é preenchida a partir de `runs` na migração. Bancos v1 continuam legíveis.

## Frontend sem troca de framework

HTML/JS na mesma origem evita Node no caminho principal. O modo guiado serializa para a DSL 1.0; o JSON avançado é a representação canônica quando o formulário não cobre um campo.

## Python 3.13

As dependências lockadas instalaram e os testes unitários passaram em Windows com CPython 3.13.3. O CI mantém 3.12 no Ubuntu com E2E e adiciona 3.13 (Ubuntu e Windows) sem Playwright, para não fingir cobertura de navegador não executada nesses jobs.

## Replay

Valida schema, hash da submissão e o contrato de evidência. Não reexecuta solvers nem interpreta artefatos como código.

## Fora desta rodada

Lean, intervalos, tradução por LLM, OpenTelemetry/OTLP, fila multi-processo com leases distribuídos, e Docker E2E no Windows. Lean/intervalos permanecem explicitamente `not implemented`.

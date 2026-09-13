# Decisões da evolução 0.6

## Interface como laboratório científico

O inglês passa a ser a língua do produto. A home deixa de ser um dashboard de três colunas com saúde do sistema em primeiro plano. A jornada é exemplo guiado → narrativa → verificação → garantia. MathML e SVG são locais e curados; gráficos ilustrativos não são certificados. O exemplo de dissipação amortecida permanece `ABSTAIN` (proof hole), sem aceite algébrico disfarçado.

# Decisões da evolução 0.5

## Anexo e matriz antes de novas plataformas

O texto original do checklist 10/10 ficou em `docs/annex/ORIGINAL_CHECKLIST.md`. A matriz em `docs/TRACEABILITY.json` atribui IDs estáveis sem apagar alternativas (Alethe, LFSC, Dedukti, Kafka, NATS, etc.). Notas 9/10 e 3/10 do anexo são opinião do autor, não auditoria.

## Campo e licença permanecem decisões humanas

Nome do campo: *Verified Science* ou *Formal Scientific Computing*. Licença: Apache 2.0, MIT, AGPL ou dual. Modelo: open source puro, open core ou fundação. Nenhuma dessas escolhas foi feita nesta fatia.

## Lean não pode certificar por omissão

Exportações anteriores eram comentários; um `lean` instalado poderia aceitar o arquivo vazio. A exportação agora declara `theorem natalia_obligation` com `sorry` explícito. O adapter classifica falhas e recusa certificado. O caminho certificado local continua `natalia.kernel`.

## Frontend e mensageria

HTML/JS permanece. Kafka, NATS e Redis não foram instalados juntos só para cumprir lista. NATS/Postgres continuam companheiros de Compose.

# Decisões da evolução 0.4


## Contrato de confiança antes de novos backends

O núcleo desta fatia é separar job, conclusão e garantia. Fast permanece o caminho SMT. Certified usa `natalia.kernel` (fragmento polinomial). Z3 não gera aceite Certified. Lean é exportação opcional; `sorry` é rejeitado; toolchain ausente não é mascarada.

## Perfil distribuído de integração, sem cloud paga

Autenticação por API key, isolamento por tenant derivado da credencial, artefatos em disco, outbox SQLite, SSE. PostgreSQL e NATS entram no Compose/Helm como companheiros opcionais; o store exercitado continua SQLite. Não há cliente NATS nesta entrega.

## Frontend

HTML/JS na mesma origem. Fast/Certified e recheck cabem no laboratório atual; troca de framework não foi justificada.

## Fora desta rodada

Mathlib pinado, Alethe/LFSC, OTLP, billing, OIDC completo, gVisor, leaderboard público, ingestão OCR, LLM.


## Fila com claim atômico no mesmo processo

`POST /api/jobs` enfileira (`origin=queue`). Um dispatcher no ciclo de vida da API faz claim `queued → running` com `lease_token`. `POST /api/runs` permanece síncrono (`origin=http-wait`) para não competir pela mesma reserva. Jobs `queued` sobrevivem a reinício; jobs `running` falham operacionalmente. Semântica **at-least-once**. Não há exatamente-uma-vez.

## PhysVerifyBench v0.1

193 instâncias sintéticas, 25 famílias, splits por família. Rótulo matemático e comportamento esperado do sistema são campos distintos. O solver avaliado não é a única fonte de verdade: os templates foram justificados a priori e depois checados. Meta de 200 não foi preenchida com clones. O conjunto é público no repositório — não é holdout oculto.

## Intervalos

Enclosure com `Fraction` em caixa `domain_min`/`domain_max`. Sem caixa, o adapter não entra na agregação. Um enclosure “consistente” permanece `unknown` (não é certificado global). Conflito SMT certificado vs enclosure refutado produz `ABSTAIN`.

## Lean

Não há toolchain Lean 4 neste ambiente. O adapter declara indisponibilidade. Não há respostas fixas fingindo kernel.

## Fora desta rodada

Tradução por LLM, OTLP, PhysLean, holdout com custódia separada, teste de usabilidade com participantes, Grafana exercitado nesta máquina.

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

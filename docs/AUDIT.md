# Auditoria acionável (evolução 0.4)

Inspeção do código em 2026-09-12, branch `feat/scientific-lab-evolution` (0.3), sem presumir que o texto histórico descrevesse o binário.

| Achado | Evidência | Risco | Prioridade | Alteração | Teste de aceite |
| --- | --- | --- | --- | --- | --- |
| Job `succeeded` misturável com aceite científico na UI | `jobs.py` documenta a distinção; UI mostrava sobretudo `verdict` | Usuário trata execução ok como teorema | P0 | Contrato `natalia-trust-1.0` + campos `conclusion`/`guarantee_level` | Fast `x**2>=0` → ACCEPTED + SMT_RELATIVE |
| Sem caminho certificado independente | `lean.py` só `probe`; DECISIONS: Lean ausente | Aceite SMT lido como certificado | P0 | Kernel polinomial + modo Certified | Certified `x**2>=0` KERNEL_CHECKED; energia com `m>0` não desce para SMT |
| Sem isolamento entre organizações | API sem auth; `GET /api/runs/{id}` global | Vazamento em qualquer bind não loopback | P0 | Perfil `distributed` com API keys; `tenant_id` derivado da chave | Org B recebe 404 no job de A |
| Fila e eventos no mesmo processo | Dispatcher asyncio + SQLite | Crash entre estado e evento | P1 | Outbox na mesma transação que `transition` | Job queued grava `job_queued` |
| Lease obsoleto | `require_lease` já existia | Worker zumbi concluir | P1 | Teste explícito de lease errado | `transition` com lease `expired` falha |
| Quotas só globais | `max_queue` por processo | Um tenant enche a fila | P1 | `NATALIA_TENANT_QUEUE` em voo (queued+running) | Segundo job 429 |
| Cache/fingerprint só do JSON | `input_sha256` sem modo | Risco futuro de reusar Fast | P2 | `cache_fingerprint` inclui modo e contrato | Campo presente no relatório |
| OTEL anunciável demais | Spans locais, não OTLP | Documentação à frente do código | P2 | README declara spans locais; OTLP continua opcional/não embutido | capabilities sem fingir OTLP |
| Helm/NATS/Postgres não existiam | só Compose SQLite | Aparência de plataforma sem fatia | P2 | Helm de teste + Compose `distributed` opcional; execução real continua SQLite local | `helm template` / compose config |

Limitações de **capacidade** (não são defeitos): fragmento kernel pequeno; Lean opcional; sem NATS cliente; Postgres não é o store padrão; sem OCR; sem LLM; PhysVerifyBench público.

Limitações de **garantia**: SMT não é certificado; kernel não é Lean; recheck não prova fidelidade textual; hash não autentica origem.

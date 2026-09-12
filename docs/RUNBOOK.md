# Operação local

## Configuração

| Variável | Padrão nativo | Efeito |
| --- | --- | --- |
| `NATALIA_DB_PATH` | `data/natalia.db` | Arquivo SQLite |
| `NATALIA_MAX_WORKERS` | `2` | Capacidade simultânea, entre 1 e 8 |
| `GRAFANA_ADMIN_PASSWORD` | `local-change-me` | Administração do Grafana via Compose |
| `NATALIA_CHROMIUM_PATH` | navegador Playwright | Executável opcional nos testes E2E |

A API não carrega `.env` automaticamente. Exporte variáveis no shell (`$env:NATALIA_DB_PATH=...` no PowerShell). Compose fixa a localização interna do banco em `/data/natalia.db`.

## Diagnóstico

| Sintoma | Ação |
| --- | --- |
| UI não abre | Consulte stdout e `GET /health/live`; confirme a porta 8000 |
| Readiness 503 | Verifique acesso/espaço no diretório do banco e versão de schema |
| HTTP 429 | Dois workers ocupados; respeite `Retry-After`; não aumente capacidade sem memória disponível |
| HTTP 422 | Leia o caminho do campo; dimensões devem ser sete strings racionais |
| `INVALID` | Abra evidência de compilação; corrija sintaxe/unidades |
| `ABSTAIN` por orçamento | Aumente `budget_ms` até 15.000 ou reduza a expressão; não interprete como refutação |
| Premissas contraditórias | Revise domínio e hipóteses; não há aceite por vacuidade |
| Domínio não demonstrado | Declare condições como `x != 0`; não elimine a singularidade por simplificação |
| `worker_failure` | Correlacione logs; preserve o JSON para reproduzir; não é evidência matemática |
| Erro 500 na submissão | Execução/persistência falhou; examine disco/permissões e reproduza localmente |
| Métricas zeradas após restart | Contadores Prometheus são por processo; histórico SQLite permanece |
| Script E2E sem navegador | Instale Chromium pelo Playwright ou configure `NATALIA_CHROMIUM_PATH` |

## Logs e métricas

`verification_completed` contém `run_id`, `trace_id`, `request_id`, `verdict`, `duration_ms`. `http_request` usa rota normalizada, método, status e duração; não imprime título, LaTeX ou corpo da submissão. Spans com timestamps, duração, oracle e IDs ficam no relatório exportável. Hash e IDs são proveniência, não assinatura criptográfica de um certificado.

`/metrics` expõe contagem HTTP, histogramas de latência, execuções por veredito, obrigações por oracle/status e workers ativos. IDs de usuário/execução não são labels. O dashboard provisionado mostra vazão, p95, vereditos, workers e falhas HTTP. Readiness verifica SQLite, não completa uma prova de saúde de cada solver.

Sugestões de alertas para etapa cloud: readiness falhando, 5xx sustentado, saturação, aumento de timeout e storage próximo do limite. Não foram instalados canais de alerta nem enviados avisos externos.

## Backup e restauração nativos

```bash
python scripts/backup.py backups/natalia-2026-09-12.db
```

A API de backup do SQLite inclui o estado consistente do WAL. Não copie apenas `natalia.db` enquanto o serviço estiver gravando. Não sobrescreva backups: o script exige um destino novo.

Para restaurar, pare a API e configure `NATALIA_DB_PATH` apontando para uma **cópia** do backup em um diretório gravável. Reinicie e verifique histórico/readiness. Nenhum comando destrutivo de restauração é automatizado nesta etapa.

Em Compose, o banco reside no volume nomeado; use a API SQLite de backup dentro do contêiner e copie o arquivo resultante com `docker compose cp`. Exemplo:

```bash
docker compose exec natalia python -c "import sqlite3; a=sqlite3.connect('/data/natalia.db'); b=sqlite3.connect('/tmp/backup.db'); a.backup(b); b.close(); a.close()"
docker compose cp natalia:/tmp/backup.db ./backup.db
```

## Limites operacionais

Conexões em andamento são jobs SQLite. Após reinício, `queued`/`running` viram `failed` com `interrupted_by_restart` — sem veredito científico. Cancelamento pede o término do worker; se o processo já devolveu o resultado, o documento persistido prevalece. Retenção: sem exclusão automática; backups via `python scripts/backup.py` e cópia via `python scripts/restore.py`.

O Compose é uma receita de teste local. Antes de cloud, executar as etapas de identidade, isolamento, limites, retenção e recuperação do roadmap.

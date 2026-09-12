# Contribuir

Use Python 3.12 ou 3.13, os lockfiles e uma branch. No Windows, prefira `scripts/setup.ps1`. Rode `ruff check .`, `pytest -q`, `python scripts/benchmark.py` e, para alterações de interface, `python scripts/e2e.py`.

A prioridade é evitar conclusões mais fortes que a evidência. Um novo oracle precisa declarar fragmento, domínio, resultado desconhecido, orçamento e base de confiança. Adicione casos negativos (incluindo premissas inconsistentes e singularidades), não apenas exemplos demonstráveis. Nunca trate timeout, simplificação ou saída textual de modelo como prova.

Mantenha a DSL versionada e rejeite campos inesperados. Não introduza avaliação de strings como código. Mudanças no armazenamento devem ter migração e teste de leitura dos dados anteriores. Não registre conteúdos de submissões em logs ou labels de métricas.

Métricas de pesquisa exigem corpus rotulado, splits e metodologia explícita. Os exemplos da entrega local são regressões e não sustentam alegações de calibração ou generalização.

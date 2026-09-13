# Evolução por entregas verificáveis

## Etapa 1 — baseline local (este PR)

Critério: um pesquisador consegue instalar, executar os exemplos, editar a DSL, obter evidências, reabrir o histórico e acompanhar o sistema localmente. Testes automatizados cobrem falsos aceites evitáveis, parsing hostil, domínio, contrapremissas, persistência, concorrência e timeout. Interface sem CDN e sem segredo externo.

Limites intencionais: formalização manual, sem Lean/Arb, CAS consultivo, política determinística, sem calibração, sem autenticação ou fila. Não se promete verificar física geral.

## Etapa 1.1 — robustez antes da cloud

- Adicionar CI em Windows/macOS e smoke tests de wheel, instalação limpa e backup/restauração.
- Ampliar regressões com propriedades algébricas geradas, revisão independente do encoding e casos de singularidades compostas.
- Introduzir protocolo tipado comum de evidência por oracle; capturar timings também nas falhas de despacho.
- Implementar jobs persistentes, idempotência, cancelamento e estados `queued/running/completed/failed`.
- Migrar dependências para locks com hashes, fixar imagens por digest e automatizar atualização/auditoria.
- Separar tradução/formalização de execução, mantendo revisão explícita antes de despachar.

## Etapa 1.2 — laboratório guiado, dados e fila local (este PR)

Critério: jornada sem JSON, catálogo com procedência, benchmark público distinto da suíte unitária, jobs com claim, intervalos só com caixa racional, Lean declarado ausente quando não há toolchain.

## Etapa 1.3 — confiança, certificado polinomial e isolamento (este PR)

Critério: contrato `natalia-trust-1.0`; Fast ≠ Certified; recheck independente do kernel; duas organizações no perfil `distributed` não leem jobs uma da outra; modo local sem auth em loopback preservado.

Gate: testes de política, kernel, tenants, lease, outbox e quotas, além da regressão 0.3.


## Etapa 2 — cloud, provedor a escolher

Escolher provedor após medir CPU/RAM/latência, volume de dados, orçamento, localização e requisitos de identidade. Não há recursos cloud provisionados neste PR.

Arquitetura candidata: API stateless e frontend na mesma origem; fila durável; workers isolados com quotas por execução; PostgreSQL; armazenamento de evidências; OpenTelemetry para logs/métricas/traces; secrets gerenciados. Separar namespace/tenant, exigir autenticação e autorização, limitar origem e tamanho de submissões e definir retenção.

Gate de publicação: testes de isolamento entre usuários, idempotência, carga, backup/restauração, alertas, custos máximos, retenção, segredos e runbook de rollback. A escolha de cloud e o deploy constituem uma entrega posterior.

## Etapa 3 — força dos verificadores

- Lean 4 / PhysLean com versão fixada, prova exportável e checagem pelo kernel; sem `sorry`, axiomas não aprovados ou execução arbitrária fornecida pelo usuário.
- Arb/MPFI com arredondamento rigoroso e evidência de domínio; checker de testemunhas algébricas.
- Modelar proveniência e conflitos de forma explícita: resultados contraditórios acionam investigação, sem ocultar divergências de formalização/domínio.
- Ampliar DSL para fragmentos assintóticos com domínio comprovado, unidades naturais e invariantes.

Gate: casos conhecidos positivos/negativos, certificados replayáveis e revisão independente da base de confiança.

## Etapa 4 — tradução e pesquisa experimental

1. Tradução de LaTeX por adapter de modelo configurável; limites, timeout e custo; nenhuma promoção automática de texto para verdade.
2. Revisão humana da formalização e registro de divergências semânticas.
3. Construção de PhysFidelityBench separado de PhysVerifyBench, com origem/licenças, anotação, splits e prevenção de vazamento.
4. Comparar baseline determinística com roteamento orientado a custo; só então treinar política POMDP/RLVR.
5. Calibrar em conjunto separado; medir risco-cobertura, false accepts, false refutes, ECE/Brier e custo com intervalos de incerteza.

Gate: nenhum percentual de confiança apresentado sem protocolo de calibração avaliado. Os volumes e metas do texto original são objetivos de pesquisa, não resultados desta entrega.

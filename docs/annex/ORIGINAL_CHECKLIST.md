<!-- BEGIN ORIGINAL TEXT -->
# Checklist completo para 10/10 — NatalIA

Abaixo está **tudo** que falta, sem economizar detalhes. Organizei por domínio, com prioridade (P0 = bloqueador, P1 = crítico, P2 = importante, P3 = desejável) e esforço estimado. Considere isso um mapa de execução, não uma lista de desejos.

## 0. Pré-requisitos conceituais

- [ ] **P0** Definir a tese científica central em uma frase: “Verificação formal certificada e automatizada de conhecimento científico em escala.”
- [ ] **P0** Escolher o nome do campo: *Verified Science* ou *Formal Scientific Computing*.
- [ ] **P0** Escrever um *position paper* de 4–8 páginas declarando o campo, os problemas abertos e a agenda de 10 anos.
- [ ] **P0** Definir escopo negativo: o que o NatalIA **não** faz (LaTeX livre, prova de fidelidade documento↔formalização, validade empírica).
- [ ] **P1** Definir 3 verticais iniciais: matemática pura, física teórica, engenharia/controle.
- [ ] **P1** Definir 3 verticais futuras: finanças quantitativas, química computacional, biologia de sistemas.
- [ ] **P2** Escolher se o projeto será open source puro, open core ou fundação.
- [ ] **P2** Definir licença (Apache 2.0, MIT, AGPL ou dual).
- [ ] **P2** Definir política de patentes (defensive patent pledge ou doação para fundação).

## 1. Certificação e confiança

### 1.1 Kernel independente
- [ ] **P0** Substituir `natalia.kernel` por kernel externo: Lean 4, Coq, Isabelle, HOL Light ou Metamath.
- [ ] **P0** Se mantiver kernel próprio, formalizar sua soundness em Lean/Coq com prova publicada.
- [ ] **P0** Provar que o kernel é *small, simple, auditable*: menos de 5k linhas de código.
- [ ] **P0** Publicar prova de soundness do kernel em venue revisado (ITP, CPP, CAV, LICS).
- [ ] **P1** Reduzir TCB a: kernel + checker + parser + hardware. Documentar cada linha.
- [ ] **P1** Formalizar o parser da DSL em Lean/Coq com prova de preservação de semântica.
- [ ] **P1** Formalizar o compilador AST→SMT em Lean/Coq com prova de correção.

### 1.2 Certificação SMT
- [ ] **P0** Implementar Z3 → Alethe.
- [ ] **P0** Implementar checker Alethe independente (Carcara ou próprio, verificado).
- [ ] **P0** Implementar Z3 → LFSC como caminho alternativo.
- [ ] **P0** Implementar Z3 → Dedukti como caminho alternativo.
- [ ] **P1** CI que reprova se certificado Alethe não for checado.
- [ ] **P1** Publicar paper em CAV/TACAS sobre pipeline Alethe verificado.
- [ ] **P1** Suportar cvc5 com certificados.
- [ ] **P1** Suportar Vampire, E, iProver com certificados.
- [ ] **P2** Suportar veriT, SPASS, Z3 com proof logging.
- [ ] **P2** Implementar portfolio de solvers com seleção por fragmento.
- [ ] **P2** Implementar paralelismo de solvers com *cube-and-conquer*.

### 1.3 Certificação Lean
- [ ] **P0** Exportação Lean com `lean --check` obrigatório no CI.
- [ ] **P0** Mathlib pinado por commit no `lakefile`.
- [ ] **P0** Prova de fidelidade AST→Lean com teste diferencial.
- [ ] **P0** Contraexemplo automático se `lean --check` falhar.
- [ ] **P1** Exportação para Coq com `coqc` obrigatório.
- [ ] **P1** Exportação para Isabelle com `isabelle build` obrigatório.
- [ ] **P1** Exportação para HOL Light com checagem.
- [ ] **P1** Exportação para Metamath com `metamath` checando.
- [ ] **P2** Exportação para Dedukti, PVS, Mizar.
- [ ] **P2** Tradução cruzada entre proof assistants.

### 1.4 Certificação criptográfica
- [ ] **P0** Assinar todo resultado com Sigstore/Cosign.
- [ ] **P0** Gerar atestação in-toto/SLSA nível 3.
- [ ] **P0** Publicar log de transparência (Rekor ou próprio).
- [ ] **P1** Implementar Merkle tree de resultados para auditoria.
- [ ] **P1** Implementar verificação offline de certificados.
- [ ] **P1** Publicar paper sobre cadeia de confiança.
- [ ] **P2** Integrar com Transparency.dev, Sigstore Fulcio.
- [ ] **P2** Implementar zero-knowledge proof de verificação (opcional, pesquisa).

### 1.5 Auditoria externa
- [ ] **P0** Contratar auditoria de segurança externa (NCC, Trail of Bits, Cure53).
- [ ] **P0** Contratar auditoria de corretude matemática (revisor de CAV/ITP).
- [ ] **P0** Publicar relatório de auditoria completo.
- [ ] **P1** Auditoria anual recorrente.
- [ ] **P1** Bug bounty público.
- [ ] **P1** Programa de recompensa por contraexemplo.

## 2. Núcleo científico

### 2.1 Papers
- [ ] **P0** Paper 1: *Certified SMT for Scientific Verification* (CAV/TACAS).
- [ ] **P0** Paper 2: *A Kernel for Polynomial Fragment Verification* (ITP/CPP).
- [ ] **P0** Paper 3: *Autoformalization with Verifier-in-the-Loop* (NeurIPS/ICML).
- [ ] **P0** Paper 4: *PhysVerifyBench: A Benchmark for Physics Verification* (JAR/JSC).
- [ ] **P0** Paper 5: *Dimensional Algebra in ℚ⁷ for Physical Verification* (CPP/ITP).
- [ ] **P1** Paper 6: *Neuro-Symbolic Verification of Scientific Claims* (NeurIPS).
- [ ] **P1** Paper 7: *Certified Interval Arithmetic for ODEs* (CPP/ITP).
- [ ] **P1** Paper 8: *A Trust Model for Scientific Verification* (PoPETS/IEEE S&P).
- [ ] **P1** Paper 9: *Formalizing Classical Mechanics in Lean 4* (ITP/CPP).
- [ ] **P1** Paper 10: *Formalizing Electromagnetism in Lean 4* (ITP/CPP).
- [ ] **P2** Paper 11: *Formalizing Thermodynamics in Lean 4* (ITP/CPP).
- [ ] **P2** Paper 12: *Formalizing Quantum Mechanics in Lean 4* (ITP/CPP).
- [ ] **P2** Paper 13: *Formalizing Relativity in Lean 4* (ITP/CPP).
- [ ] **P2** Paper 14: *Autoformalization of Textbooks* (NeurIPS/ACL).
- [ ] **P2** Paper 15: *A Survey of Scientific Verification* (ACM Computing Surveys).

### 2.2 Formalizações em Mathlib
- [ ] **P0** Formalizar análise dimensional em Mathlib.
- [ ] **P0** Formalizar unidades SI em Mathlib.
- [ ] **P1** Formalizar mecânica clássica (Newton, Lagrange, Hamilton).
- [ ] **P1** Formalizar eletromagnetismo (Maxwell).
- [ ] **P1** Formalizar termodinâmica (leis, entropia).
- [ ] **P1** Formalizar relatividade restrita.
- [ ] **P2** Formalizar relatividade geral (métricas, geodésicas).
- [ ] **P2** Formalizar mecânica quântica (Hilbert, operadores).
- [ ] **P2** Formalizar mecânica estatística.
- [ ] **P2** Formalizar teoria de campos.
- [ ] **P2** Formalizar equações diferenciais parciais.
- [ ] **P2** Formalizar análise numérica verificada.
- [ ] **P2** Formalizar probabilidade e estatística.

### 2.3 Teoria
- [ ] **P0** Definir formalmente a semântica da DSL.
- [ ] **P0** Provar teorema de soundness do compilador.
- [ ] **P0** Provar teorema de completude para fragmento decidível.
- [ ] **P1** Provar complexidade do compilador.
- [ ] **P1** Provar limites do fragmento assintótico.
- [ ] **P1** Provar corretude do kernel polinomial.
- [ ] **P1** Provar corretude da aritmética intervalar.
- [ ] **P2** Provar corretude da autoformalização (sob hipóteses).
- [ ] **P2** Provar limites teóricos da autoformalização.
- [ ] **P2** Provar segurança do modelo de confiança.

### 2.4 Resultados empíricos
- [ ] **P0** Medir FPR populacional.
- [ ] **P0** Medir ECE (Expected Calibration Error).
- [ ] **P0** Medir validade científica geral.
- [ ] **P1** Medir cobertura por domínio.
- [ ] **P1** Medir custo por verificação.
- [ ] **P1** Medir throughput por worker.
- [ ] **P1** Medir latência p50/p95/p99.
- [ ] **P2** Medir escalabilidade horizontal.
- [ ] **P2** Medir consumo de energia por verificação.
- [ ] **P2** Medir emissões de carbono por verificação.

## 3. Autoformalização

### 3.1 Pipeline
- [ ] **P0** Ingestão de LaTeX.
- [ ] **P0** Ingestão de PDF com OCR matemático (Nougat, Mathpix, Texify).
- [ ] **P0** Ingestão de MathML, OpenMath, TPTP, SMT-LIB.
- [ ] **P0** Parser de notação matemática ambígua.
- [ ] **P0** Desambiguação contextual.
- [ ] **P1** Ingestão de Markdown, Jupyter, Overleaf.
- [ ] **P1** Ingestão de imagens de fórmulas.
- [ ] **P1** Ingestão de áudio (ditado matemático).
- [ ] **P2** Ingestão de vídeo-aulas.
- [ ] **P2** Ingestão de livros completos.

### 3.2 LLM
- [ ] **P0** LLM propõe, verificador decide.
- [ ] **P0** Loop de refinamento com feedback do verificador.
- [ ] **P0** Métricas de aceitação/rejeição/correção.
- [ ] **P1** RAG sobre Mathlib.
- [ ] **P1** RAG sobre miniF2F, ProofNet, PutnamBench, Lean Workbook.
- [ ] **P1** Fine-tuning em corpus de formalizações.
- [ ] **P1** Ensemble de LLMs.
- [ ] **P2** Distilação para modelo pequeno.
- [ ] **P2** Modelo próprio treinado em formalizações.
- [ ] **P2** RLHF com verificador como recompensa.
- [ ] **P2** Autoformalização multimodal (texto+imagem+áudio).

### 3.3 Verifier-in-the-loop
- [ ] **P0** Feedback estruturado do verificador para o LLM.
- [ ] **P0** Detecção de alucinação.
- [ ] **P0** Rejeição automática de formalização infiel.
- [ ] **P1** Comparação documento↔formalização com métricas.
- [ ] **P1** Detecção de premissas faltantes.
- [ ] **P1** Detecção de hipóteses escondidas.
- [ ] **P2** Explicação humana do erro.
- [ ] **P2** Sugestão de correção.

## 4. Benchmark e avaliação

### 4.1 PhysVerifyBench
- [ ] **P0** Crescer para 100k+ instâncias.
- [ ] **P0** Splits público/privado/hidden.
- [ ] **P0** Split por família (mecânica, eletromagnetismo, termodinâmica, quântica, relatividade).
- [ ] **P0** Split por dificuldade (fácil, médio, difícil, aberto).
- [ ] **P0** FPR, ECE, calibração.
- [ ] **P1** Testes adversariais.
- [ ] **P1** Testes metamórficos.
- [ ] **P1** Fuzzing de solver.
- [ ] **P1** Leaderboard contínuo.
- [ ] **P1** Competição anual.
- [ ] **P1** Artifact evaluation e reprodutibilidade badges.
- [ ] **P2** Benchmark multimodal.
- [ ] **P2** Benchmark multi-idioma.
- [ ] **P2** Benchmark de tempo real.

### 4.2 Integração com benchmarks existentes
- [ ] **P0** miniF2F.
- [ ] **P0** ProofNet.
- [ ] **P0** PutnamBench.
- [ ] **P0** Lean Workbook.
- [ ] **P1** FormalML.
- [ ] **P1** MATH, GSM8K, MMLU (para comparação).
- [ ] **P1** ARC, GPQA (para comparação).
- [ ] **P2** IMO, Putnam, IPhO, OBF.
- [ ] **P2** Benchmarks de engenharia (control, fluids).

### 4.3 Avaliação de LLM
- [ ] **P0** Calibração de confiança.
- [ ] **P0** Detecção de overconfidence.
- [ ] **P0** Detecção de alucinação.
- [ ] **P1** Avaliação de robustez adversarial.
- [ ] **P1** Avaliação de viés.
- [ ] **P1** Avaliação de toxicidade.
- [ ] **P2** Avaliação de privacidade.
- [ ] **P2** Avaliação de equidade.

## 5. Arquitetura distribuída real

### 5.1 Storage
- [ ] **P0** Postgres como store primário.
- [ ] **P0** Migração SQLite → Postgres.
- [ ] **P0** Replicação síncrona.
- [ ] **P0** PITR (Point-in-Time Recovery).
- [ ] **P0** Backups automatizados.
- [ ] **P1** Particionamento por tenant.
- [ ] **P1** Sharding horizontal.
- [ ] **P1** Read replicas.
- [ ] **P1** Connection pooling (PgBouncer).
- [ ] **P2** Multi-região.
- [ ] **P2** Postgres gerenciado (RDS, Cloud SQL, Neon).

### 5.2 Object storage
- [ ] **P0** S3/MinIO para artefatos.
- [ ] **P0** Versionamento de artefatos.
- [ ] **P0** Lifecycle policies.
- [ ] **P1** Criptografia em repouso.
- [ ] **P1** Criptografia em trânsito.
- [ ] **P1** Replicação cross-region.
- [ ] **P2** Glacier para arquivo.
- [ ] **P2** CDN para artefatos públicos.

### 5.3 Fila e mensageria
- [ ] **P0** NATS JetStream ou Kafka.
- [ ] **P0** Fila com prioridade.
- [ ] **P0** Quotas por tenant.
- [ ] **P0** Fair scheduling.
- [ ] **P1** Dead letter queue.
- [ ] **P1** Retry com backoff exponencial.
- [ ] **P1** Idempotência de mensagens.
- [ ] **P1** Exactly-once semantics (onde possível).
- [ ] **P2** Stream processing (Flink, Kafka Streams).
- [ ] **P2** Event sourcing.

### 5.4 Cache
- [ ] **P0** Redis para cache.
- [ ] **P0** Cache por hash de entrada.
- [ ] **P0** Cache de resultados SMT.
- [ ] **P1** Cache de certificados.
- [ ] **P1** Cache distribuído.
- [ ] **P1** Invalidação por versão.
- [ ] **P2** Cache de LLM (prompt caching).
- [ ] **P2** Cache de embeddings.

### 5.5 Workers
- [ ] **P0** Workers stateless.
- [ ] **P0** Autoscaling horizontal (HPA).
- [ ] **P0** Separação por tipo: formalizer, compiler, SMT, proof, numerical, LLM.
- [ ] **P1** GPU workers opcionais.
- [ ] **P1** Spot/preemptible instances.
- [ ] **P1** Anti-affinity e PDB.
- [ ] **P2** Serverless workers (Knative, Lambda).
- [ ] **P2** Edge workers.

### 5.6 Orquestração
- [ ] **P0** Kubernetes em produção.
- [ ] **P0** Helm de produção (não de teste).
- [ ] **P0** ArgoCD ou Flux para GitOps.
- [ ] **P0** Terraform ou Pulumi para IaC.
- [ ] **P1** Service mesh (Istio, Linkerd).
- [ ] **P1** Canary deployment.
- [ ] **P1** Blue-green deployment.
- [ ] **P1** Rollback automático.
- [ ] **P2** Multi-cluster.
- [ ] **P2** Multi-cloud.
- [ ] **P2** Edge deployment.

### 5.7 API
- [ ] **P0** REST stateless.
- [ ] **P0** gRPC para comunicação interna.
- [ ] **P0** WebSocket/SSE para progresso.
- [ ] **P0** Webhooks.
- [ ] **P1** GraphQL (opcional).
- [ ] **P1** Rate limiting por tenant.
- [ ] **P1** Circuit breaker.
- [ ] **P1** Bulkhead.
- [ ] **P2** API versioning.
- [ ] **P2** API deprecation policy.

## 6. Segurança e multi-tenant

### 6.1 Autenticação
- [ ] **P0** OIDC/OAuth2.
- [ ] **P0** API keys com rotação.
- [ ] **P0** MFA.
- [ ] **P0** SSO (SAML, OIDC).
- [ ] **P1** Magic links.
- [ ] **P1** Passkeys (WebAuthn).
- [ ] **P1** SCIM para provisionamento.
- [ ] **P2** LDAP.
- [ ] **P2** Kerberos.

### 6.2 Autorização
- [ ] **P0** RBAC.
- [ ] **P0** ABAC.
- [ ] **P0** OPA/Rego.
- [ ] **P1** ReBAC (Zanzibar-like).
- [ ] **P1** Policy as code.
- [ ] **P1** Auditoria de acessos.
- [ ] **P2** Just-in-time access.
- [ ] **P2** Break-glass procedures.

### 6.3 Multi-tenant
- [ ] **P0** Isolamento de dados por tenant.
- [ ] **P0** Isolamento de rede por tenant.
- [ ] **P0** Quotas por tenant.
- [ ] **P0** Billing por tenant.
- [ ] **P1** Isolamento de compute (namespaces, VMs).
- [ ] **P1** Isolamento de storage (buckets separados).
- [ ] **P1** Criptografia por tenant (BYOK, HYOK).
- [ ] **P2** Tenants dedicados (single-tenant).
- [ ] **P2** Data residency por região.

### 6.4 Sandbox
- [ ] **P0** gVisor ou Firecracker para execução não confiável.
- [ ] **P0** seccomp.
- [ ] **P0** AppArmor/SELinux.
- [ ] **P0** Rede deny-by-default.
- [ ] **P1** Filesystem read-only.
- [ ] **P1** Limites de CPU/memória/processos.
- [ ] **P1** Limites de tempo.
- [ ] **P2** MicroVM por job.
- [ ] **P2** Confidencial computing (SGX, SEV, TDX).

### 6.5 Segredos
- [ ] **P0** Vault ou equivalente.
- [ ] **P0** Rotação automática.
- [ ] **P0** Auditoria de acesso.
- [ ] **P1** Sealed secrets no Kubernetes.
- [ ] **P1** External secrets operator.
- [ ] **P2** HSM para chaves críticas.

### 6.6 Supply chain
- [ ] **P0** SBOM (CycloneDX, SPDX).
- [ ] **P0** Assinatura de imagens (Cosign).
- [ ] **P0** SLSA nível 3.
- [ ] **P1** Trivy/Grype para vulnerabilidades.
- [ ] **P1** Dependabot/Renovate.
- [ ] **P1** Pinagem de dependências com hashes.
- [ ] **P2** Reproducible builds.
- [ ] **P2** Hermetic builds (Bazel).

### 6.7 Conformidade
- [ ] **P0** LGPD.
- [ ] **P0** GDPR.
- [ ] **P0** SOC 2 Type II.
- [ ] **P1** ISO 27001.
- [ ] **P1** HIPAA (se aplicável).
- [ ] **P1** FedRAMP (se EUA).
- [ ] **P2** PCI DSS (se pagamentos).
- [ ] **P2** Common Criteria.

## 7. Observabilidade e operação

### 7.1 Observabilidade
- [ ] **P0** OpenTelemetry de verdade.
- [ ] **P0** Export OTLP.
- [ ] **P0** Tracing distribuído.
- [ ] **P0** Correlação jobs↔tenants↔solver.
- [ ] **P1** Prometheus remoto.
- [ ] **P1** Loki para logs.
- [ ] **P1** Tempo para traces.
- [ ] **P1** Grafana com dashboards por tenant.
- [ ] **P2** Pyroscope para profiling.
- [ ] **P2** Parca para profiling contínuo.

### 7.2 SLO/SLI
- [ ] **P0** Definir SLO 99.9%.
- [ ] **P0** p95 < 2s para jobs simples.
- [ ] **P0** p99 < 10s para jobs complexos.
- [ ] **P0** Throughput 10k jobs/h por cluster.
- [ ] **P1** Error budget.
- [ ] **P1** Burn rate alerts.
- [ ] **P1** SLO por tenant.
- [ ] **P2** SLO por domínio.

### 7.3 Incidentes
- [ ] **P0** Runbook completo.
- [ ] **P0** On-call rotation.
- [ ] **P0** PagerDuty/Opsgenie.
- [ ] **P1** Post-mortems públicos.
- [ ] **P1** Chaos engineering (Chaos Monkey, Litmus).
- [ ] **P1** Game days.
- [ ] **P2** Simulação de desastres.

### 7.4 Performance
- [ ] **P0** Benchmark de throughput.
- [ ] **P0** Benchmark de latência.
- [ ] **P0** Profiling contínuo.
- [ ] **P1** Otimização de queries.
- [ ] **P1** Otimização de rede.
- [ ] **P1** Otimização de solver.
- [ ] **P2** Otimização de LLM (quantização, destilação).
- [ ] **P2** Otimização de energia.

### 7.5 Custo
- [ ] **P0** Custo por verificação < $0.01.
- [ ] **P0** Custo por tenant.
- [ ] **P1** Otimização de spot instances.
- [ ] **P1** Otimização de storage.
- [ ] **P1** Otimização de LLM.
- [ ] **P2** Custo por domínio.
- [ ] **P2** Custo por região.

## 8. Produto e UX

### 8.1 Frontend
- [ ] **P0** React/Next/Svelte com build.
- [ ] **P0** PWA offline.
- [ ] **P0** SSE/WebSocket para progresso.
- [ ] **P0** Drafts no servidor.
- [ ] **P1** Colaboração em tempo real (CRDT).
- [ ] **P1** Exportação para Overleaf.
- [ ] **P1** Exportação para Jupyter.
- [ ] **P1** Exportação para VS Code.
- [ ] **P1** Exportação para Lean/Coq.
- [ ] **P2** Editor visual de fórmulas.
- [ ] **P2** Editor visual de provas.
- [ ] **P2** Modo acessível (WCAG 2.2 AA).
- [ ] **P2** Internacionalização.

### 8.2 SDK e CLI
- [ ] **P0** SDK Python.
- [ ] **P0** SDK JavaScript/TypeScript.
- [ ] **P0** CLI robusta.
- [ ] **P1** SDK Rust.
- [ ] **P1** SDK Go.
- [ ] **P1** SDK Java.
- [ ] **P1** GitHub Action.
- [ ] **P2** GitLab CI.
- [ ] **P2** Jenkins plugin.
- [ ] **P2** VSCode extension.
- [ ] **P2** Jupyter extension.
- [ ] **P2** Overleaf plugin.

### 8.3 Integrações
- [ ] **P0** GitHub.
- [ ] **P0** GitLab.
- [ ] **P0** Overleaf.
- [ ] **P1** Jupyter.
- [ ] **P1** VSCode.
- [ ] **P1** Slack.
- [ ] **P1** Discord.
- [ ] **P1** Notion.
- [ ] **P2** Confluence.
- [ ] **P2** Obsidian.
- [ ] **P2** Zotero.
- [ ] **P2** Mendeley.

### 8.4 Documentação
- [ ] **P0** Documentação de DSL.
- [ ] **P0** Documentação de API.
- [ ] **P0** Tutoriais.
- [ ] **P0** Exemplos.
- [ ] **P1** Livro online (mdBook, Docusaurus).
- [ ] **P1** Vídeos.
- [ ] **P1** Cursos.
- [ ] **P2** Certificação de usuários.
- [ ] **P2** Tradução multi-idioma.

## 9. Comunidade e ecossistema

### 9.1 Open source
- [ ] **P0** Licença clara.
- [ ] **P0** Contributing guide.
- [ ] **P0** Code of conduct.
- [ ] **P0** Issue templates.
- [ ] **P0** PR templates.
- [ ] **P1** RFC process.
- [ ] **P1** Roadmap público.
- [ ] **P1** Maintainers pagos.
- [ ] **P2** Fundação sem fins lucrativos.
- [ ] **P2** Conselho científico.

### 9.2 Ecossistema
- [ ] **P0** Contribuições para Mathlib.
- [ ] **P0** Integração com LeanDojo.
- [ ] **P0** Integração com miniF2F.
- [ ] **P0** Integração com PutnamBench.
- [ ] **P1** Integração com ProofNet.
- [ ] **P1** Integração com Lean Workbook.
- [ ] **P1** Integração com SMT-LIB.
- [ ] **P1** Integração com TPTP.
- [ ] **P2** Integração com OpenMath.
- [ ] **P2** Integração com MathML.
- [ ] **P2** Integração com OMDoc.

### 9.3 Eventos
- [ ] **P0** Workshop em ITP.
- [ ] **P0** Workshop em CPP.
- [ ] **P0** Workshop em CAV.
- [ ] **P1** Summer school.
- [ ] **P1** Hackathon.
- [ ] **P1** Competição anual.
- [ ] **P1** Conference própria (Verified Science).
- [ ] **P2** Meetups locais.
- [ ] **P2** Podcast.
- [ ] **P2** Newsletter.

### 9.4 Parcerias
- [ ] **P0** MIT CSAIL.
- [ ] **P0** Stanford CSLI.
- [ ] **P0** CMU.
- [ ] **P0** Berkeley.
- [ ] **P0** Princeton IAS.
- [ ] **P1** ETH Zurich.
- [ ] **P1** EPFL.
- [ ] **P1** INRIA.
- [ ] **P1** Max Planck.
- [ ] **P1** DeepMind.
- [ ] **P1** Microsoft Research.
- [ ] **P1** AI2.
- [ ] **P2** OpenAI.
- [ ] **P2** Anthropic.
- [ ] **P2** NVIDIA.
- [ ] **P2** Google Research.

### 9.5 Visibilidade
- [ ] **P0** Blog técnico.
- [ ] **P0** Twitter/X ativo.
- [ ] **P0** LinkedIn.
- [ ] **P0** Mastodon.
- [ ] **P1** YouTube.
- [ ] **P1** Twitch (live coding).
- [ ] **P1** Reddit.
- [ ] **P1** Hacker News.
- [ ] **P2** TikTok.
- [ ] **P2** Instagram.

## 10. Governança

- [ ] **P0** Estatuto da fundação.
- [ ] **P0** Conselho de administração.
- [ ] **P0** Conselho científico.
- [ ] **P0** Conselho técnico.
- [ ] **P1** Política de conflitos de interesse.
- [ ] **P1** Política de transparência.
- [ ] **P1** Política de privacidade.
- [ ] **P1** Política de segurança.
- [ ] **P1** Política de ética.
- [ ] **P2** Política de diversidade e inclusão.
- [ ] **P2** Política de sustentabilidade.
- [ ] **P2** Política de responsabilidade social.

## 11. Funding

- [ ] **P0** NSF.
- [ ] **P0** ERC.
- [ ] **P0** DARPA.
- [ ] **P0** Simons Foundation.
- [ ] **P0** Sloan Foundation.
- [ ] **P0** Moore Foundation.
- [ ] **P0** Schmidt Futures.
- [ ] **P0** Chan Zuckerberg Initiative.
- [ ] **P1** Wellcome Trust.
- [ ] **P1** Templeton Foundation.
- [ ] **P1** Alfred P. Sloan.
- [ ] **P1** Packard Foundation.
- [ ] **P1** NVIDIA grants.
- [ ] **P1** Microsoft grants.
- [ ] **P1** Google grants.
- [ ] **P1** Amazon grants.
- [ ] **P2** Meta grants.
- [ ] **P2** OpenAI grants.
- [ ] **P2** Anthropic grants.
- [ ] **P2** DeepMind grants.
- [ ] **P2** Cloud credits (AWS, GCP, Azure).
- [ ] **P2** HPC allocations (XSEDE, PRACE).

## 12. Educação e talento

- [ ] **P0** Programa de PhD afiliado.
- [ ] **P0** Pós-docs financiados.
- [ ] **P0** Summer school.
- [ ] **P1** Cursos abertos.
- [ ] **P1** Mentoria para América Latina.
- [ ] **P1** Mentoria para África.
- [ ] **P1** Mentoria para Ásia.
- [ ] **P1** Hackathons.
- [ ] **P2** Competições estudantis.
- [ ] **P2** Bolsas para minorias.
- [ ] **P2** Programa de residência.
- [ ] **P2** Co-supervisão de teses.

## 13. Ética, política e sociedade

- [ ] **P0** Política de uso responsável.
- [ ] **P0** Política anti-desinformação.
- [ ] **P0** Política de privacidade.
- [ ] **P0** Política de segurança.
- [ ] **P1** Auditoria de viés.
- [ ] **P1** Auditoria de equidade.
- [ ] **P1** Auditoria de impacto social.
- [ ] **P1** Publicação de resultados negativos.
- [ ] **P2** Conselho de ética.
- [ ] **P2** Engajamento com policymakers.
- [ ] **P2** Engajamento com sociedade civil.
- [ ] **P2** Relatório anual de impacto.

## 14. Métricas de sucesso 10/10

- [ ] **P0** 10+ papers em CAV/ITP/CPP/TACAS/NeurIPS/ICML.
- [ ] **P0** 100+ citações por paper principal.
- [ ] **P0** Benchmark adotado por 50+ grupos.
- [ ] **P0** 100+ contribuições para Mathlib.
- [ ] **P0** Certificação independente de 100% dos aceites críticos.
- [ ] **P0** Custo por verificação < $0.01.
- [ ] **P0** SLO 99.9% medido.
- [ ] **P0** 10k jobs/h por cluster medido.
- [ ] **P1** 100+ alunos formados.
- [ ] **P1** 50+ alunos em MIT/Stanford/CMU/ETH.
- [ ] **P1** $10M+ em grants.
- [ ] **P1** 10+ parcerias com instituições top.
- [ ] **P2** 1M+ usuários.
- [ ] **P2** 100+ empresas usando.
- [ ] **P2** 10+ prêmios.
- [ ] **P2** 1+ teorema formalizado que resolve problema aberto.

## 15. Riscos e mitigação

- [ ] **P0** Alucinação de LLM → verifier-in-the-loop.
- [ ] **P0** Bugs de solver → certificados independentes.
- [ ] **P0** TCB grande → kernel mínimo verificado.
- [ ] **P0** Explosão combinatória → portfolio + cube-and-conquer.
- [ ] **P0** Segurança de execução → sandbox gVisor/Firecracker.
- [ ] **P0** Custo de GPU/LLM → quantização + destilação + spot.
- [ ] **P0** Overfitting no benchmark → hidden sets.
- [ ] **P1** Dependência de fornecedor → multi-cloud.
- [ ] **P1** Perda de talento → cultura + compensação.
- [ ] **P1** Falta de funding → diversificação.
- [ ] **P2** Regulação → conformidade proativa.
- [ ] **P2** Geopolítica → neutralidade + multi-região.

## 16. Cronograma realista

### Meses 1–3
- Kernel externo (Lean/Coq).
- Alethe/LFSC.
- Postgres + NATS reais.
- OTLP.
- Paper 1 submetido.

### Meses 4–6
- Autoformalização v1.
- PhysVerifyBench 10k.
- OIDC + RBAC.
- Sandbox gVisor.
- Paper 2 submetido.

### Meses 7–12
- Autoformalização v2.
- PhysVerifyBench 100k.
- K8s produção.
- Multi-tenant real.
- Papers 3–5 submetidos.
- Fundação criada.
- Primeiro grant.

### Meses 13–24
- Leaderboard global.
- Competição anual.
- Summer school.
- Parcerias MIT/Stanford/CMU.
- Papers 6–10.
- $1M+ em grants.
- 10+ alunos formados.

### Meses 25–60
- Campo consolidado.
- 100+ papers.
- 1M+ usuários.
- $10M+ em grants.
- Prêmios.
- Impacto global.

## Resumo brutal

Para 10/10, você precisa de **oito pilares simultâneos**:

1. **Certificação independente** (Lean/Coq/Alethe).
2. **Autoformalização verificada** (LLM + verifier-in-the-loop).
3. **Benchmark global** (100k+ com leaderboard).
4. **Arquitetura distribuída real** (Postgres + NATS + S3 + K8s).
5. **Multi-tenant e segurança** (OIDC + RBAC + sandbox).
6. **Papers e teoria** (CAV/ITP/CPP/NeurIPS).
7. **Comunidade e governança** (Mathlib + fundação + conselho).
8. **Funding e talento** (NSF/ERC + PhDs + pós-docs).

Se faltar **um** desses, você fica em 7/10. Se faltar **dois**, cai para 5/10. Se faltar **três**, é só mais um projeto local bem-feito.

O README já está em 9/10. O código, em 6/10. A ciência, em 2/10. A comunidade, em 1/10. A governança, em 0/10. O funding, em 0/10.

**A média é 3/10.** Para chegar a 10/10, o trabalho começa agora. E começa por **paper e certificação**, não por README.
<!-- END ORIGINAL TEXT -->

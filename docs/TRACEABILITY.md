# Matriz de rastreabilidade NatalIA

Matriz gerada a partir de `docs/annex/ORIGINAL_CHECKLIST.md` e dos requisitos adicionais do preâmbulo.
SHA-256 do anexo: `520ee5972fc77692a5d2ab83934b23e1128e1b9f771a62c6b1f1e36268caab53`.
Registros: **587**.

Estimates assume one software engineer plus intermittent scientific review, not a funded lab. They are not commitments of calendar time or budget.

Prioridades P0–P3 são as do anexo. `execution_stage` (A–F) é ordem de dependência, não renumeração.

## Contagens

Por estado: bloqueado=7, dependente de decisão=5, em execução=1, implementado sem validação=40, não aplicável=3, não iniciado=511, validado=20

Por prioridade original: P0=259, P1=192, P2=134, P3=2

A tabela completa está em [TRACEABILITY.json](TRACEABILITY.json). Abaixo, um registro por identificador.

| ID | P | Estado | Natureza | Seção | Texto original |
| --- | --- | --- | --- | --- | --- |
| `ADD-01` | P0 | validado | engenharia | 1. Contrato de preservação | Gerar matriz de rastreabilidade com identificador estável para cada requisito, inclusive parágrafos, tabelas, riscos e conclusões. |
| `ADD-02` | P0 | validado | governança | 1. Contrato de preservação | Preservar itens, nomes, alternativas tecnológicas, prioridades, números, cronogramas e ambições do anexo. |
| `ADD-03` | P0 | validado | governança | 1. Contrato de preservação | Manter o anexo integral em controle de versão e verificar sua preservação. |
| `ADD-04` | P0 | validado | governança | 1. Contrato de preservação | Identificar cada complemento do preâmbulo como requisito adicional. |
| `ADD-05` | P0 | validado | governança | 1. Contrato de preservação | Estimativas informam hipóteses de equipe e faixas otimista/provável/pessimista, sem tratar prazos como fatos. |
| `ADD-06` | P0 | validado | engenharia | 2. Diagnóstico obrigatório | Diagnosticar README, código, testes, CI, dependências, licenças, frontend, API, workers e documentação com evidências por caminho. |
| `ADD-07` | P0 | validado | engenharia | 2. Diagnóstico obrigatório | Reproduzir inicialização e fluxo completo entrada → validação → job → execução → resultado → evidência → visualização. |
| `ADD-08` | P0 | validado | pesquisa | 2. Diagnóstico obrigatório | Tratar notas numéricas e comparações institucionais do anexo como opiniões do autor, não auditoria independente. |
| `ADD-09` | P0 | validado | engenharia | 3. Semântica de resultados | Preservar ACCEPTED, REFUTED, INVALID, ABSTAIN e separar estado lógico do estado operacional do job. |
| `ADD-10` | P0 | implementado sem validação | engenharia | 3. Semântica de resultados | Modelar FAST, CERTIFIED e AUTOFORMALIZED como dimensões com contratos explícitos. |
| `ADD-11` | P0 | validado | engenharia | 3. Semântica de resultados | Implementar ao menos um caminho vertical real de certificação para um fragmento delimitado, sem enfraquecer a proposição. |
| `ADD-12` | P0 | validado | engenharia | 3. Esclarecimentos | Falha de proof assistant não implica falsidade nem contraexemplo automático; classificar syntax/type/dependency/timeout/incomplete. |
| `ADD-13` | P0 | validado | engenharia | 3. Esclarecimentos | Tratar `lean --check` como intenção de checagem obrigatória, não como garantia de flag CLI. |
| `ADD-14` | P0 | validado | pesquisa | 3. Esclarecimentos | Núcleo pequeno não é correto por si; delimitar o que foi provado e o que permanece no TCB. |
| `ADD-15` | P0 | implementado sem validação | engenharia | 4. Arquitetura evolutiva | Manter três perfis documentados: local, distribuído de desenvolvimento e produção. |
| `ADD-16` | P0 | implementado sem validação | engenharia | 4. Arquitetura evolutiva | Escolher tecnologias centrais por ADR; preservar alternativas no registro sem instalar todas simultaneamente. |
| `ADD-17` | P1 | não iniciado | engenharia | 4. Arquitetura evolutiva | Definir migração SQLite/Postgres com corte, consistência e jobs em execução, sem escrita dupla improvisada. |
| `ADD-18` | P0 | implementado sem validação | engenharia | 5. Segurança | Modelar ameaças específicas e isolar execução de entrada não confiável. |
| `ADD-19` | P0 | validado | engenharia | 5. Segurança | Obter tenant de identidade autenticada no servidor; não confiar em tenant_id do cliente. |
| `ADD-20` | P0 | não iniciado | governança | 5. Segurança | Não alegar SLSA/SOC2/ISO sem avaliação de versão, escopo e evidências. |
| `ADD-21` | P1 | não iniciado | engenharia | 6. Autoformalização | Pipeline versionado ingestão → extração → AST → fidelidade → obrigação → prova → checagem. |
| `ADD-22` | P0 | não iniciado | pesquisa | 6. Autoformalização | Registrar origem, licença e limitações de todo dataset; não redistribuir sem autorização. |
| `ADD-23` | P1 | implementado sem validação | produto | 7. Interface | Tela inicial com criar verificação, exemplo, importar, jobs e resultados; fluxo guiado. |
| `ADD-24` | P2 | não iniciado | produto | 7. Interface | Acessibilidade WCAG 2.2 AA, i18n, teclado e estados vazio/erro; certificação não pode ser simulada na UI. |
| `ADD-25` | P0 | não iniciado | pesquisa | 8. Avaliação | Toda meta vira protocolo mensurável; 99.9%, p95, 10k jobs/h e US$0.01 permanecem objetivos até medição. |
| `ADD-26` | P0 | não iniciado | pesquisa | 9. Pesquisa | Não fabricar teoremas, provas, parcerias, grants ou submissões; contatos externos exigem autorização humana. |
| `ADD-27` | P0 | implementado sem validação | engenharia | 10. Etapas | Etapa A — base reproduzível com gate de outra pessoa iniciar e conferir evidências. |
| `ADD-28` | P0 | implementado sem validação | engenharia | 10. Etapas | Etapa B — confiança demonstrável com fragmento certificado, testes negativos e limites documentados. |
| `ADD-29` | P1 | não iniciado | engenharia | 10. Etapas | Etapa C — distribuição e isolamento (Postgres, mensageria escolhida, API/worker, identidade, quotas). |
| `ADD-30` | P1 | não iniciado | produto | 10. Etapas | Etapa D — produto e dados (UX guiada, catálogo, autoformalização delimitada). |
| `ADD-31` | P2 | não iniciado | operação | 10. Etapas | Etapa E — produção (IaC, backups, canary, carga) sem confundir teste local com prontidão. |
| `ADD-32` | P2 | não iniciado | governança | 10. Etapas | Etapa F — programa contínuo científico, comunitário e de financiamento. |
| `ADD-33` | P0 | validado | produto | 11. Entregáveis | README com limites de escala, Fast≠Certified, guia Windows PowerShell e Linux/macOS, Python 3.12/3.13. |
| `ADD-34` | P0 | em execução | engenharia | 11. Entregáveis | PR revisável com problema, mudanças, validação, riscos e pendências. |
| `ADD-35` | P0 | validado | engenharia | 11. Entregáveis | Relatório final separa concluído e validado; implementado sem validação; planejado; bloqueado. |
| `ANN-0-001` | P0 | implementado sem validação | pesquisa | 0. Pré-requisitos conceituais | Definir a tese científica central em uma frase: “Verificação formal certificada e automatizada de conhecimento científico em escala.” |
| `ANN-0-002` | P0 | dependente de decisão | pesquisa | 0. Pré-requisitos conceituais | Escolher o nome do campo: *Verified Science* ou *Formal Scientific Computing*. |
| `ANN-0-003` | P0 | implementado sem validação | pesquisa | 0. Pré-requisitos conceituais | Escrever um *position paper* de 4–8 páginas declarando o campo, os problemas abertos e a agenda de 10 anos. |
| `ANN-0-004` | P0 | implementado sem validação | pesquisa | 0. Pré-requisitos conceituais | Definir escopo negativo: o que o NatalIA **não** faz (LaTeX livre, prova de fidelidade documento↔formalização, validade empírica). |
| `ANN-0-005` | P1 | implementado sem validação | pesquisa | 0. Pré-requisitos conceituais | Definir 3 verticais iniciais: matemática pura, física teórica, engenharia/controle. |
| `ANN-0-006` | P1 | implementado sem validação | pesquisa | 0. Pré-requisitos conceituais | Definir 3 verticais futuras: finanças quantitativas, química computacional, biologia de sistemas. |
| `ANN-0-007` | P2 | dependente de decisão | pesquisa | 0. Pré-requisitos conceituais | Escolher se o projeto será open source puro, open core ou fundação. |
| `ANN-0-008` | P2 | dependente de decisão | pesquisa | 0. Pré-requisitos conceituais | Definir licença (Apache 2.0, MIT, AGPL ou dual). |
| `ANN-0-009` | P2 | dependente de decisão | pesquisa | 0. Pré-requisitos conceituais | Definir política de patentes (defensive patent pledge ou doação para fundação). |
| `ANN-1.1-001` | P0 | não iniciado | pesquisa | 1.1 Kernel independente | Substituir `natalia.kernel` por kernel externo: Lean 4, Coq, Isabelle, HOL Light ou Metamath. |
| `ANN-1.1-002` | P0 | não iniciado | pesquisa | 1.1 Kernel independente | Se mantiver kernel próprio, formalizar sua soundness em Lean/Coq com prova publicada. |
| `ANN-1.1-003` | P0 | implementado sem validação | pesquisa | 1.1 Kernel independente | Provar que o kernel é *small, simple, auditable*: menos de 5k linhas de código. |
| `ANN-1.1-004` | P0 | não iniciado | pesquisa | 1.1 Kernel independente | Publicar prova de soundness do kernel em venue revisado (ITP, CPP, CAV, LICS). |
| `ANN-1.1-005` | P1 | implementado sem validação | pesquisa | 1.1 Kernel independente | Reduzir TCB a: kernel + checker + parser + hardware. Documentar cada linha. |
| `ANN-1.1-006` | P1 | não iniciado | pesquisa | 1.1 Kernel independente | Formalizar o parser da DSL em Lean/Coq com prova de preservação de semântica. |
| `ANN-1.1-007` | P1 | não iniciado | pesquisa | 1.1 Kernel independente | Formalizar o compilador AST→SMT em Lean/Coq com prova de correção. |
| `ANN-1.2-001` | P0 | não iniciado | engenharia | 1.2 Certificação SMT | Implementar Z3 → Alethe. |
| `ANN-1.2-002` | P0 | não iniciado | engenharia | 1.2 Certificação SMT | Implementar checker Alethe independente (Carcara ou próprio, verificado). |
| `ANN-1.2-003` | P0 | não iniciado | engenharia | 1.2 Certificação SMT | Implementar Z3 → LFSC como caminho alternativo. |
| `ANN-1.2-004` | P0 | não iniciado | engenharia | 1.2 Certificação SMT | Implementar Z3 → Dedukti como caminho alternativo. |
| `ANN-1.2-005` | P1 | não iniciado | engenharia | 1.2 Certificação SMT | CI que reprova se certificado Alethe não for checado. |
| `ANN-1.2-006` | P1 | não iniciado | engenharia | 1.2 Certificação SMT | Publicar paper em CAV/TACAS sobre pipeline Alethe verificado. |
| `ANN-1.2-007` | P1 | não iniciado | engenharia | 1.2 Certificação SMT | Suportar cvc5 com certificados. |
| `ANN-1.2-008` | P1 | não iniciado | engenharia | 1.2 Certificação SMT | Suportar Vampire, E, iProver com certificados. |
| `ANN-1.2-009` | P2 | não iniciado | engenharia | 1.2 Certificação SMT | Suportar veriT, SPASS, Z3 com proof logging. |
| `ANN-1.2-010` | P2 | não iniciado | engenharia | 1.2 Certificação SMT | Implementar portfolio de solvers com seleção por fragmento. |
| `ANN-1.2-011` | P2 | não iniciado | engenharia | 1.2 Certificação SMT | Implementar paralelismo de solvers com *cube-and-conquer*. |
| `ANN-1.3-001` | P0 | implementado sem validação | engenharia | 1.3 Certificação Lean | Exportação Lean com `lean --check` obrigatório no CI. |
| `ANN-1.3-002` | P0 | não iniciado | engenharia | 1.3 Certificação Lean | Mathlib pinado por commit no `lakefile`. |
| `ANN-1.3-003` | P0 | não iniciado | engenharia | 1.3 Certificação Lean | Prova de fidelidade AST→Lean com teste diferencial. |
| `ANN-1.3-004` | P0 | implementado sem validação | engenharia | 1.3 Certificação Lean | Contraexemplo automático se `lean --check` falhar. |
| `ANN-1.3-005` | P1 | não iniciado | engenharia | 1.3 Certificação Lean | Exportação para Coq com `coqc` obrigatório. |
| `ANN-1.3-006` | P1 | não iniciado | engenharia | 1.3 Certificação Lean | Exportação para Isabelle com `isabelle build` obrigatório. |
| `ANN-1.3-007` | P1 | não iniciado | engenharia | 1.3 Certificação Lean | Exportação para HOL Light com checagem. |
| `ANN-1.3-008` | P1 | não iniciado | engenharia | 1.3 Certificação Lean | Exportação para Metamath com `metamath` checando. |
| `ANN-1.3-009` | P2 | não iniciado | engenharia | 1.3 Certificação Lean | Exportação para Dedukti, PVS, Mizar. |
| `ANN-1.3-010` | P2 | não iniciado | engenharia | 1.3 Certificação Lean | Tradução cruzada entre proof assistants. |
| `ANN-1.4-001` | P0 | não iniciado | engenharia | 1.4 Certificação criptográfica | Assinar todo resultado com Sigstore/Cosign. |
| `ANN-1.4-002` | P0 | não iniciado | engenharia | 1.4 Certificação criptográfica | Gerar atestação in-toto/SLSA nível 3. |
| `ANN-1.4-003` | P0 | não iniciado | engenharia | 1.4 Certificação criptográfica | Publicar log de transparência (Rekor ou próprio). |
| `ANN-1.4-004` | P1 | não iniciado | engenharia | 1.4 Certificação criptográfica | Implementar Merkle tree de resultados para auditoria. |
| `ANN-1.4-005` | P1 | não iniciado | engenharia | 1.4 Certificação criptográfica | Implementar verificação offline de certificados. |
| `ANN-1.4-006` | P1 | não iniciado | engenharia | 1.4 Certificação criptográfica | Publicar paper sobre cadeia de confiança. |
| `ANN-1.4-007` | P2 | não iniciado | engenharia | 1.4 Certificação criptográfica | Integrar com Transparency.dev, Sigstore Fulcio. |
| `ANN-1.4-008` | P2 | não iniciado | engenharia | 1.4 Certificação criptográfica | Implementar zero-knowledge proof de verificação (opcional, pesquisa). |
| `ANN-1.5-001` | P0 | bloqueado | colaboração externa | 1.5 Auditoria externa | Contratar auditoria de segurança externa (NCC, Trail of Bits, Cure53). |
| `ANN-1.5-002` | P0 | bloqueado | colaboração externa | 1.5 Auditoria externa | Contratar auditoria de corretude matemática (revisor de CAV/ITP). |
| `ANN-1.5-003` | P0 | não iniciado | colaboração externa | 1.5 Auditoria externa | Publicar relatório de auditoria completo. |
| `ANN-1.5-004` | P1 | não iniciado | colaboração externa | 1.5 Auditoria externa | Auditoria anual recorrente. |
| `ANN-1.5-005` | P1 | bloqueado | colaboração externa | 1.5 Auditoria externa | Bug bounty público. |
| `ANN-1.5-006` | P1 | não iniciado | colaboração externa | 1.5 Auditoria externa | Programa de recompensa por contraexemplo. |
| `ANN-2.1-001` | P0 | não iniciado | pesquisa | 2.1 Papers | Paper 1: *Certified SMT for Scientific Verification* (CAV/TACAS). |
| `ANN-2.1-002` | P0 | não iniciado | pesquisa | 2.1 Papers | Paper 2: *A Kernel for Polynomial Fragment Verification* (ITP/CPP). |
| `ANN-2.1-003` | P0 | não iniciado | pesquisa | 2.1 Papers | Paper 3: *Autoformalization with Verifier-in-the-Loop* (NeurIPS/ICML). |
| `ANN-2.1-004` | P0 | não iniciado | pesquisa | 2.1 Papers | Paper 4: *PhysVerifyBench: A Benchmark for Physics Verification* (JAR/JSC). |
| `ANN-2.1-005` | P0 | não iniciado | pesquisa | 2.1 Papers | Paper 5: *Dimensional Algebra in ℚ⁷ for Physical Verification* (CPP/ITP). |
| `ANN-2.1-006` | P1 | não iniciado | pesquisa | 2.1 Papers | Paper 6: *Neuro-Symbolic Verification of Scientific Claims* (NeurIPS). |
| `ANN-2.1-007` | P1 | não iniciado | pesquisa | 2.1 Papers | Paper 7: *Certified Interval Arithmetic for ODEs* (CPP/ITP). |
| `ANN-2.1-008` | P1 | não iniciado | pesquisa | 2.1 Papers | Paper 8: *A Trust Model for Scientific Verification* (PoPETS/IEEE S&P). |
| `ANN-2.1-009` | P1 | não iniciado | pesquisa | 2.1 Papers | Paper 9: *Formalizing Classical Mechanics in Lean 4* (ITP/CPP). |
| `ANN-2.1-010` | P1 | não iniciado | pesquisa | 2.1 Papers | Paper 10: *Formalizing Electromagnetism in Lean 4* (ITP/CPP). |
| `ANN-2.1-011` | P2 | não iniciado | pesquisa | 2.1 Papers | Paper 11: *Formalizing Thermodynamics in Lean 4* (ITP/CPP). |
| `ANN-2.1-012` | P2 | não iniciado | pesquisa | 2.1 Papers | Paper 12: *Formalizing Quantum Mechanics in Lean 4* (ITP/CPP). |
| `ANN-2.1-013` | P2 | não iniciado | pesquisa | 2.1 Papers | Paper 13: *Formalizing Relativity in Lean 4* (ITP/CPP). |
| `ANN-2.1-014` | P2 | não iniciado | pesquisa | 2.1 Papers | Paper 14: *Autoformalization of Textbooks* (NeurIPS/ACL). |
| `ANN-2.1-015` | P2 | não iniciado | pesquisa | 2.1 Papers | Paper 15: *A Survey of Scientific Verification* (ACM Computing Surveys). |
| `ANN-2.2-001` | P0 | não iniciado | pesquisa | 2.2 Formalizações em Mathlib | Formalizar análise dimensional em Mathlib. |
| `ANN-2.2-002` | P0 | não iniciado | pesquisa | 2.2 Formalizações em Mathlib | Formalizar unidades SI em Mathlib. |
| `ANN-2.2-003` | P1 | não iniciado | pesquisa | 2.2 Formalizações em Mathlib | Formalizar mecânica clássica (Newton, Lagrange, Hamilton). |
| `ANN-2.2-004` | P1 | não iniciado | pesquisa | 2.2 Formalizações em Mathlib | Formalizar eletromagnetismo (Maxwell). |
| `ANN-2.2-005` | P1 | não iniciado | pesquisa | 2.2 Formalizações em Mathlib | Formalizar termodinâmica (leis, entropia). |
| `ANN-2.2-006` | P1 | não iniciado | pesquisa | 2.2 Formalizações em Mathlib | Formalizar relatividade restrita. |
| `ANN-2.2-007` | P2 | não iniciado | pesquisa | 2.2 Formalizações em Mathlib | Formalizar relatividade geral (métricas, geodésicas). |
| `ANN-2.2-008` | P2 | não iniciado | pesquisa | 2.2 Formalizações em Mathlib | Formalizar mecânica quântica (Hilbert, operadores). |
| `ANN-2.2-009` | P2 | não iniciado | pesquisa | 2.2 Formalizações em Mathlib | Formalizar mecânica estatística. |
| `ANN-2.2-010` | P2 | não iniciado | pesquisa | 2.2 Formalizações em Mathlib | Formalizar teoria de campos. |
| `ANN-2.2-011` | P2 | não iniciado | pesquisa | 2.2 Formalizações em Mathlib | Formalizar equações diferenciais parciais. |
| `ANN-2.2-012` | P2 | não iniciado | pesquisa | 2.2 Formalizações em Mathlib | Formalizar análise numérica verificada. |
| `ANN-2.2-013` | P2 | não iniciado | pesquisa | 2.2 Formalizações em Mathlib | Formalizar probabilidade e estatística. |
| `ANN-2.3-001` | P0 | não iniciado | pesquisa | 2.3 Teoria | Definir formalmente a semântica da DSL. |
| `ANN-2.3-002` | P0 | não iniciado | pesquisa | 2.3 Teoria | Provar teorema de soundness do compilador. |
| `ANN-2.3-003` | P0 | não iniciado | pesquisa | 2.3 Teoria | Provar teorema de completude para fragmento decidível. |
| `ANN-2.3-004` | P1 | não iniciado | pesquisa | 2.3 Teoria | Provar complexidade do compilador. |
| `ANN-2.3-005` | P1 | não iniciado | pesquisa | 2.3 Teoria | Provar limites do fragmento assintótico. |
| `ANN-2.3-006` | P1 | não iniciado | pesquisa | 2.3 Teoria | Provar corretude do kernel polinomial. |
| `ANN-2.3-007` | P1 | não iniciado | pesquisa | 2.3 Teoria | Provar corretude da aritmética intervalar. |
| `ANN-2.3-008` | P2 | não iniciado | pesquisa | 2.3 Teoria | Provar corretude da autoformalização (sob hipóteses). |
| `ANN-2.3-009` | P2 | não iniciado | pesquisa | 2.3 Teoria | Provar limites teóricos da autoformalização. |
| `ANN-2.3-010` | P2 | não iniciado | pesquisa | 2.3 Teoria | Provar segurança do modelo de confiança. |
| `ANN-2.4-001` | P0 | não iniciado | pesquisa | 2.4 Resultados empíricos | Medir FPR populacional. |
| `ANN-2.4-002` | P0 | não iniciado | pesquisa | 2.4 Resultados empíricos | Medir ECE (Expected Calibration Error). |
| `ANN-2.4-003` | P0 | não iniciado | pesquisa | 2.4 Resultados empíricos | Medir validade científica geral. |
| `ANN-2.4-004` | P1 | não iniciado | pesquisa | 2.4 Resultados empíricos | Medir cobertura por domínio. |
| `ANN-2.4-005` | P1 | não iniciado | pesquisa | 2.4 Resultados empíricos | Medir custo por verificação. |
| `ANN-2.4-006` | P1 | não iniciado | pesquisa | 2.4 Resultados empíricos | Medir throughput por worker. |
| `ANN-2.4-007` | P1 | não iniciado | pesquisa | 2.4 Resultados empíricos | Medir latência p50/p95/p99. |
| `ANN-2.4-008` | P2 | não iniciado | pesquisa | 2.4 Resultados empíricos | Medir escalabilidade horizontal. |
| `ANN-2.4-009` | P2 | não iniciado | pesquisa | 2.4 Resultados empíricos | Medir consumo de energia por verificação. |
| `ANN-2.4-010` | P2 | não iniciado | pesquisa | 2.4 Resultados empíricos | Medir emissões de carbono por verificação. |
| `ANN-3.1-001` | P0 | não iniciado | engenharia | 3.1 Pipeline | Ingestão de LaTeX. |
| `ANN-3.1-002` | P0 | não iniciado | engenharia | 3.1 Pipeline | Ingestão de PDF com OCR matemático (Nougat, Mathpix, Texify). |
| `ANN-3.1-003` | P0 | não iniciado | engenharia | 3.1 Pipeline | Ingestão de MathML, OpenMath, TPTP, SMT-LIB. |
| `ANN-3.1-004` | P0 | não iniciado | engenharia | 3.1 Pipeline | Parser de notação matemática ambígua. |
| `ANN-3.1-005` | P0 | não iniciado | engenharia | 3.1 Pipeline | Desambiguação contextual. |
| `ANN-3.1-006` | P1 | não iniciado | engenharia | 3.1 Pipeline | Ingestão de Markdown, Jupyter, Overleaf. |
| `ANN-3.1-007` | P1 | não iniciado | engenharia | 3.1 Pipeline | Ingestão de imagens de fórmulas. |
| `ANN-3.1-008` | P1 | não iniciado | engenharia | 3.1 Pipeline | Ingestão de áudio (ditado matemático). |
| `ANN-3.1-009` | P2 | não iniciado | engenharia | 3.1 Pipeline | Ingestão de vídeo-aulas. |
| `ANN-3.1-010` | P2 | não iniciado | engenharia | 3.1 Pipeline | Ingestão de livros completos. |
| `ANN-3.2-001` | P0 | não iniciado | pesquisa | 3.2 LLM | LLM propõe, verificador decide. |
| `ANN-3.2-002` | P0 | não iniciado | pesquisa | 3.2 LLM | Loop de refinamento com feedback do verificador. |
| `ANN-3.2-003` | P0 | não iniciado | pesquisa | 3.2 LLM | Métricas de aceitação/rejeição/correção. |
| `ANN-3.2-004` | P1 | não iniciado | pesquisa | 3.2 LLM | RAG sobre Mathlib. |
| `ANN-3.2-005` | P1 | não iniciado | pesquisa | 3.2 LLM | RAG sobre miniF2F, ProofNet, PutnamBench, Lean Workbook. |
| `ANN-3.2-006` | P1 | não iniciado | pesquisa | 3.2 LLM | Fine-tuning em corpus de formalizações. |
| `ANN-3.2-007` | P1 | não iniciado | pesquisa | 3.2 LLM | Ensemble de LLMs. |
| `ANN-3.2-008` | P2 | não iniciado | pesquisa | 3.2 LLM | Distilação para modelo pequeno. |
| `ANN-3.2-009` | P2 | não iniciado | pesquisa | 3.2 LLM | Modelo próprio treinado em formalizações. |
| `ANN-3.2-010` | P2 | não iniciado | pesquisa | 3.2 LLM | RLHF com verificador como recompensa. |
| `ANN-3.2-011` | P2 | não iniciado | pesquisa | 3.2 LLM | Autoformalização multimodal (texto+imagem+áudio). |
| `ANN-3.3-001` | P0 | não iniciado | engenharia | 3.3 Verifier-in-the-loop | Feedback estruturado do verificador para o LLM. |
| `ANN-3.3-002` | P0 | não iniciado | engenharia | 3.3 Verifier-in-the-loop | Detecção de alucinação. |
| `ANN-3.3-003` | P0 | não iniciado | engenharia | 3.3 Verifier-in-the-loop | Rejeição automática de formalização infiel. |
| `ANN-3.3-004` | P1 | não iniciado | engenharia | 3.3 Verifier-in-the-loop | Comparação documento↔formalização com métricas. |
| `ANN-3.3-005` | P1 | não iniciado | engenharia | 3.3 Verifier-in-the-loop | Detecção de premissas faltantes. |
| `ANN-3.3-006` | P1 | não iniciado | engenharia | 3.3 Verifier-in-the-loop | Detecção de hipóteses escondidas. |
| `ANN-3.3-007` | P2 | não iniciado | engenharia | 3.3 Verifier-in-the-loop | Explicação humana do erro. |
| `ANN-3.3-008` | P2 | não iniciado | engenharia | 3.3 Verifier-in-the-loop | Sugestão de correção. |
| `ANN-4.1-001` | P0 | não iniciado | pesquisa | 4.1 PhysVerifyBench | Crescer para 100k+ instâncias. |
| `ANN-4.1-002` | P0 | não iniciado | pesquisa | 4.1 PhysVerifyBench | Splits público/privado/hidden. |
| `ANN-4.1-003` | P0 | implementado sem validação | pesquisa | 4.1 PhysVerifyBench | Split por família (mecânica, eletromagnetismo, termodinâmica, quântica, relatividade). |
| `ANN-4.1-004` | P0 | não iniciado | pesquisa | 4.1 PhysVerifyBench | Split por dificuldade (fácil, médio, difícil, aberto). |
| `ANN-4.1-005` | P0 | não iniciado | pesquisa | 4.1 PhysVerifyBench | FPR, ECE, calibração. |
| `ANN-4.1-006` | P1 | não iniciado | pesquisa | 4.1 PhysVerifyBench | Testes adversariais. |
| `ANN-4.1-007` | P1 | não iniciado | pesquisa | 4.1 PhysVerifyBench | Testes metamórficos. |
| `ANN-4.1-008` | P1 | não iniciado | pesquisa | 4.1 PhysVerifyBench | Fuzzing de solver. |
| `ANN-4.1-009` | P1 | não iniciado | pesquisa | 4.1 PhysVerifyBench | Leaderboard contínuo. |
| `ANN-4.1-010` | P1 | não iniciado | pesquisa | 4.1 PhysVerifyBench | Competição anual. |
| `ANN-4.1-011` | P1 | não iniciado | pesquisa | 4.1 PhysVerifyBench | Artifact evaluation e reprodutibilidade badges. |
| `ANN-4.1-012` | P2 | não iniciado | pesquisa | 4.1 PhysVerifyBench | Benchmark multimodal. |
| `ANN-4.1-013` | P2 | não iniciado | pesquisa | 4.1 PhysVerifyBench | Benchmark multi-idioma. |
| `ANN-4.1-014` | P2 | não iniciado | pesquisa | 4.1 PhysVerifyBench | Benchmark de tempo real. |
| `ANN-4.2-001` | P0 | não iniciado | pesquisa | 4.2 Integração com benchmarks existentes | miniF2F. |
| `ANN-4.2-002` | P0 | não iniciado | pesquisa | 4.2 Integração com benchmarks existentes | ProofNet. |
| `ANN-4.2-003` | P0 | não iniciado | pesquisa | 4.2 Integração com benchmarks existentes | PutnamBench. |
| `ANN-4.2-004` | P0 | não iniciado | pesquisa | 4.2 Integração com benchmarks existentes | Lean Workbook. |
| `ANN-4.2-005` | P1 | não iniciado | pesquisa | 4.2 Integração com benchmarks existentes | FormalML. |
| `ANN-4.2-006` | P1 | não iniciado | pesquisa | 4.2 Integração com benchmarks existentes | MATH, GSM8K, MMLU (para comparação). |
| `ANN-4.2-007` | P1 | não iniciado | pesquisa | 4.2 Integração com benchmarks existentes | ARC, GPQA (para comparação). |
| `ANN-4.2-008` | P2 | não iniciado | pesquisa | 4.2 Integração com benchmarks existentes | IMO, Putnam, IPhO, OBF. |
| `ANN-4.2-009` | P2 | não iniciado | pesquisa | 4.2 Integração com benchmarks existentes | Benchmarks de engenharia (control, fluids). |
| `ANN-4.3-001` | P0 | não iniciado | pesquisa | 4.3 Avaliação de LLM | Calibração de confiança. |
| `ANN-4.3-002` | P0 | não iniciado | pesquisa | 4.3 Avaliação de LLM | Detecção de overconfidence. |
| `ANN-4.3-003` | P0 | não iniciado | pesquisa | 4.3 Avaliação de LLM | Detecção de alucinação. |
| `ANN-4.3-004` | P1 | não iniciado | pesquisa | 4.3 Avaliação de LLM | Avaliação de robustez adversarial. |
| `ANN-4.3-005` | P1 | não iniciado | pesquisa | 4.3 Avaliação de LLM | Avaliação de viés. |
| `ANN-4.3-006` | P1 | não iniciado | pesquisa | 4.3 Avaliação de LLM | Avaliação de toxicidade. |
| `ANN-4.3-007` | P2 | não iniciado | pesquisa | 4.3 Avaliação de LLM | Avaliação de privacidade. |
| `ANN-4.3-008` | P2 | não iniciado | pesquisa | 4.3 Avaliação de LLM | Avaliação de equidade. |
| `ANN-5.1-001` | P0 | não iniciado | engenharia | 5.1 Storage | Postgres como store primário. |
| `ANN-5.1-002` | P0 | não iniciado | engenharia | 5.1 Storage | Migração SQLite → Postgres. |
| `ANN-5.1-003` | P0 | não iniciado | engenharia | 5.1 Storage | Replicação síncrona. |
| `ANN-5.1-004` | P0 | não iniciado | engenharia | 5.1 Storage | PITR (Point-in-Time Recovery). |
| `ANN-5.1-005` | P0 | não iniciado | engenharia | 5.1 Storage | Backups automatizados. |
| `ANN-5.1-006` | P1 | não iniciado | engenharia | 5.1 Storage | Particionamento por tenant. |
| `ANN-5.1-007` | P1 | não iniciado | engenharia | 5.1 Storage | Sharding horizontal. |
| `ANN-5.1-008` | P1 | não iniciado | engenharia | 5.1 Storage | Read replicas. |
| `ANN-5.1-009` | P1 | não iniciado | engenharia | 5.1 Storage | Connection pooling (PgBouncer). |
| `ANN-5.1-010` | P2 | não iniciado | engenharia | 5.1 Storage | Multi-região. |
| `ANN-5.1-011` | P2 | não iniciado | engenharia | 5.1 Storage | Postgres gerenciado (RDS, Cloud SQL, Neon). |
| `ANN-5.2-001` | P0 | não iniciado | engenharia | 5.2 Object storage | S3/MinIO para artefatos. |
| `ANN-5.2-002` | P0 | não iniciado | engenharia | 5.2 Object storage | Versionamento de artefatos. |
| `ANN-5.2-003` | P0 | não iniciado | engenharia | 5.2 Object storage | Lifecycle policies. |
| `ANN-5.2-004` | P1 | não iniciado | engenharia | 5.2 Object storage | Criptografia em repouso. |
| `ANN-5.2-005` | P1 | não iniciado | engenharia | 5.2 Object storage | Criptografia em trânsito. |
| `ANN-5.2-006` | P1 | não iniciado | engenharia | 5.2 Object storage | Replicação cross-region. |
| `ANN-5.2-007` | P2 | não iniciado | engenharia | 5.2 Object storage | Glacier para arquivo. |
| `ANN-5.2-008` | P2 | não iniciado | engenharia | 5.2 Object storage | CDN para artefatos públicos. |
| `ANN-5.3-001` | P0 | não iniciado | engenharia | 5.3 Fila e mensageria | NATS JetStream ou Kafka. |
| `ANN-5.3-002` | P0 | não iniciado | engenharia | 5.3 Fila e mensageria | Fila com prioridade. |
| `ANN-5.3-003` | P0 | implementado sem validação | engenharia | 5.3 Fila e mensageria | Quotas por tenant. |
| `ANN-5.3-004` | P0 | não iniciado | engenharia | 5.3 Fila e mensageria | Fair scheduling. |
| `ANN-5.3-005` | P1 | não iniciado | engenharia | 5.3 Fila e mensageria | Dead letter queue. |
| `ANN-5.3-006` | P1 | não iniciado | engenharia | 5.3 Fila e mensageria | Retry com backoff exponencial. |
| `ANN-5.3-007` | P1 | não iniciado | engenharia | 5.3 Fila e mensageria | Idempotência de mensagens. |
| `ANN-5.3-008` | P1 | não iniciado | engenharia | 5.3 Fila e mensageria | Exactly-once semantics (onde possível). |
| `ANN-5.3-009` | P2 | não iniciado | engenharia | 5.3 Fila e mensageria | Stream processing (Flink, Kafka Streams). |
| `ANN-5.3-010` | P2 | não iniciado | engenharia | 5.3 Fila e mensageria | Event sourcing. |
| `ANN-5.4-001` | P0 | não iniciado | engenharia | 5.4 Cache | Redis para cache. |
| `ANN-5.4-002` | P0 | implementado sem validação | engenharia | 5.4 Cache | Cache por hash de entrada. |
| `ANN-5.4-003` | P0 | não iniciado | engenharia | 5.4 Cache | Cache de resultados SMT. |
| `ANN-5.4-004` | P1 | não iniciado | engenharia | 5.4 Cache | Cache de certificados. |
| `ANN-5.4-005` | P1 | não iniciado | engenharia | 5.4 Cache | Cache distribuído. |
| `ANN-5.4-006` | P1 | não iniciado | engenharia | 5.4 Cache | Invalidação por versão. |
| `ANN-5.4-007` | P2 | não iniciado | engenharia | 5.4 Cache | Cache de LLM (prompt caching). |
| `ANN-5.4-008` | P2 | não iniciado | engenharia | 5.4 Cache | Cache de embeddings. |
| `ANN-5.5-001` | P0 | implementado sem validação | engenharia | 5.5 Workers | Workers stateless. |
| `ANN-5.5-002` | P0 | não iniciado | engenharia | 5.5 Workers | Autoscaling horizontal (HPA). |
| `ANN-5.5-003` | P0 | não iniciado | engenharia | 5.5 Workers | Separação por tipo: formalizer, compiler, SMT, proof, numerical, LLM. |
| `ANN-5.5-004` | P1 | não iniciado | engenharia | 5.5 Workers | GPU workers opcionais. |
| `ANN-5.5-005` | P1 | não iniciado | engenharia | 5.5 Workers | Spot/preemptible instances. |
| `ANN-5.5-006` | P1 | não iniciado | engenharia | 5.5 Workers | Anti-affinity e PDB. |
| `ANN-5.5-007` | P2 | não iniciado | engenharia | 5.5 Workers | Serverless workers (Knative, Lambda). |
| `ANN-5.5-008` | P2 | não iniciado | engenharia | 5.5 Workers | Edge workers. |
| `ANN-5.6-001` | P0 | não iniciado | operação | 5.6 Orquestração | Kubernetes em produção. |
| `ANN-5.6-002` | P0 | não iniciado | operação | 5.6 Orquestração | Helm de produção (não de teste). |
| `ANN-5.6-003` | P0 | não iniciado | operação | 5.6 Orquestração | ArgoCD ou Flux para GitOps. |
| `ANN-5.6-004` | P0 | não iniciado | operação | 5.6 Orquestração | Terraform ou Pulumi para IaC. |
| `ANN-5.6-005` | P1 | não iniciado | operação | 5.6 Orquestração | Service mesh (Istio, Linkerd). |
| `ANN-5.6-006` | P1 | não iniciado | operação | 5.6 Orquestração | Canary deployment. |
| `ANN-5.6-007` | P1 | não iniciado | operação | 5.6 Orquestração | Blue-green deployment. |
| `ANN-5.6-008` | P1 | não iniciado | operação | 5.6 Orquestração | Rollback automático. |
| `ANN-5.6-009` | P2 | não iniciado | operação | 5.6 Orquestração | Multi-cluster. |
| `ANN-5.6-010` | P2 | não iniciado | operação | 5.6 Orquestração | Multi-cloud. |
| `ANN-5.6-011` | P2 | não iniciado | operação | 5.6 Orquestração | Edge deployment. |
| `ANN-5.7-001` | P0 | implementado sem validação | engenharia | 5.7 API | REST stateless. |
| `ANN-5.7-002` | P0 | não iniciado | engenharia | 5.7 API | gRPC para comunicação interna. |
| `ANN-5.7-003` | P0 | implementado sem validação | engenharia | 5.7 API | WebSocket/SSE para progresso. |
| `ANN-5.7-004` | P0 | não iniciado | engenharia | 5.7 API | Webhooks. |
| `ANN-5.7-005` | P1 | não iniciado | engenharia | 5.7 API | GraphQL (opcional). |
| `ANN-5.7-006` | P1 | não iniciado | engenharia | 5.7 API | Rate limiting por tenant. |
| `ANN-5.7-007` | P1 | não iniciado | engenharia | 5.7 API | Circuit breaker. |
| `ANN-5.7-008` | P1 | não iniciado | engenharia | 5.7 API | Bulkhead. |
| `ANN-5.7-009` | P2 | não iniciado | engenharia | 5.7 API | API versioning. |
| `ANN-5.7-010` | P2 | não iniciado | engenharia | 5.7 API | API deprecation policy. |
| `ANN-6.1-001` | P0 | não iniciado | engenharia | 6.1 Autenticação | OIDC/OAuth2. |
| `ANN-6.1-002` | P0 | implementado sem validação | engenharia | 6.1 Autenticação | API keys com rotação. |
| `ANN-6.1-003` | P0 | não iniciado | engenharia | 6.1 Autenticação | MFA. |
| `ANN-6.1-004` | P0 | não iniciado | engenharia | 6.1 Autenticação | SSO (SAML, OIDC). |
| `ANN-6.1-005` | P1 | não iniciado | engenharia | 6.1 Autenticação | Magic links. |
| `ANN-6.1-006` | P1 | não iniciado | engenharia | 6.1 Autenticação | Passkeys (WebAuthn). |
| `ANN-6.1-007` | P1 | não iniciado | engenharia | 6.1 Autenticação | SCIM para provisionamento. |
| `ANN-6.1-008` | P2 | não iniciado | engenharia | 6.1 Autenticação | LDAP. |
| `ANN-6.1-009` | P2 | não iniciado | engenharia | 6.1 Autenticação | Kerberos. |
| `ANN-6.2-001` | P0 | implementado sem validação | engenharia | 6.2 Autorização | RBAC. |
| `ANN-6.2-002` | P0 | não iniciado | engenharia | 6.2 Autorização | ABAC. |
| `ANN-6.2-003` | P0 | não iniciado | engenharia | 6.2 Autorização | OPA/Rego. |
| `ANN-6.2-004` | P1 | não iniciado | engenharia | 6.2 Autorização | ReBAC (Zanzibar-like). |
| `ANN-6.2-005` | P1 | não iniciado | engenharia | 6.2 Autorização | Policy as code. |
| `ANN-6.2-006` | P1 | não iniciado | engenharia | 6.2 Autorização | Auditoria de acessos. |
| `ANN-6.2-007` | P2 | não iniciado | engenharia | 6.2 Autorização | Just-in-time access. |
| `ANN-6.2-008` | P2 | não iniciado | engenharia | 6.2 Autorização | Break-glass procedures. |
| `ANN-6.3-001` | P0 | implementado sem validação | engenharia | 6.3 Multi-tenant | Isolamento de dados por tenant. |
| `ANN-6.3-002` | P0 | não iniciado | engenharia | 6.3 Multi-tenant | Isolamento de rede por tenant. |
| `ANN-6.3-003` | P0 | implementado sem validação | engenharia | 6.3 Multi-tenant | Quotas por tenant. |
| `ANN-6.3-004` | P0 | não iniciado | engenharia | 6.3 Multi-tenant | Billing por tenant. |
| `ANN-6.3-005` | P1 | não iniciado | engenharia | 6.3 Multi-tenant | Isolamento de compute (namespaces, VMs). |
| `ANN-6.3-006` | P1 | não iniciado | engenharia | 6.3 Multi-tenant | Isolamento de storage (buckets separados). |
| `ANN-6.3-007` | P1 | não iniciado | engenharia | 6.3 Multi-tenant | Criptografia por tenant (BYOK, HYOK). |
| `ANN-6.3-008` | P2 | não iniciado | engenharia | 6.3 Multi-tenant | Tenants dedicados (single-tenant). |
| `ANN-6.3-009` | P2 | não iniciado | engenharia | 6.3 Multi-tenant | Data residency por região. |
| `ANN-6.4-001` | P0 | não iniciado | engenharia | 6.4 Sandbox | gVisor ou Firecracker para execução não confiável. |
| `ANN-6.4-002` | P0 | não iniciado | engenharia | 6.4 Sandbox | seccomp. |
| `ANN-6.4-003` | P0 | não iniciado | engenharia | 6.4 Sandbox | AppArmor/SELinux. |
| `ANN-6.4-004` | P0 | não iniciado | engenharia | 6.4 Sandbox | Rede deny-by-default. |
| `ANN-6.4-005` | P1 | implementado sem validação | engenharia | 6.4 Sandbox | Filesystem read-only. |
| `ANN-6.4-006` | P1 | implementado sem validação | engenharia | 6.4 Sandbox | Limites de CPU/memória/processos. |
| `ANN-6.4-007` | P1 | validado | engenharia | 6.4 Sandbox | Limites de tempo. |
| `ANN-6.4-008` | P2 | não iniciado | engenharia | 6.4 Sandbox | MicroVM por job. |
| `ANN-6.4-009` | P2 | não iniciado | engenharia | 6.4 Sandbox | Confidencial computing (SGX, SEV, TDX). |
| `ANN-6.5-001` | P0 | não iniciado | operação | 6.5 Segredos | Vault ou equivalente. |
| `ANN-6.5-002` | P0 | não iniciado | operação | 6.5 Segredos | Rotação automática. |
| `ANN-6.5-003` | P0 | não iniciado | operação | 6.5 Segredos | Auditoria de acesso. |
| `ANN-6.5-004` | P1 | não iniciado | operação | 6.5 Segredos | Sealed secrets no Kubernetes. |
| `ANN-6.5-005` | P1 | não iniciado | operação | 6.5 Segredos | External secrets operator. |
| `ANN-6.5-006` | P2 | não iniciado | operação | 6.5 Segredos | HSM para chaves críticas. |
| `ANN-6.6-001` | P0 | não iniciado | engenharia | 6.6 Supply chain | SBOM (CycloneDX, SPDX). |
| `ANN-6.6-002` | P0 | não iniciado | engenharia | 6.6 Supply chain | Assinatura de imagens (Cosign). |
| `ANN-6.6-003` | P0 | não iniciado | engenharia | 6.6 Supply chain | SLSA nível 3. |
| `ANN-6.6-004` | P1 | não iniciado | engenharia | 6.6 Supply chain | Trivy/Grype para vulnerabilidades. |
| `ANN-6.6-005` | P1 | não iniciado | engenharia | 6.6 Supply chain | Dependabot/Renovate. |
| `ANN-6.6-006` | P1 | não iniciado | engenharia | 6.6 Supply chain | Pinagem de dependências com hashes. |
| `ANN-6.6-007` | P2 | não iniciado | engenharia | 6.6 Supply chain | Reproducible builds. |
| `ANN-6.6-008` | P2 | não iniciado | engenharia | 6.6 Supply chain | Hermetic builds (Bazel). |
| `ANN-6.7-001` | P0 | não iniciado | governança | 6.7 Conformidade | LGPD. |
| `ANN-6.7-002` | P0 | não iniciado | governança | 6.7 Conformidade | GDPR. |
| `ANN-6.7-003` | P0 | não iniciado | governança | 6.7 Conformidade | SOC 2 Type II. |
| `ANN-6.7-004` | P1 | não iniciado | governança | 6.7 Conformidade | ISO 27001. |
| `ANN-6.7-005` | P1 | não iniciado | governança | 6.7 Conformidade | HIPAA (se aplicável). |
| `ANN-6.7-006` | P1 | não iniciado | governança | 6.7 Conformidade | FedRAMP (se EUA). |
| `ANN-6.7-007` | P2 | não iniciado | governança | 6.7 Conformidade | PCI DSS (se pagamentos). |
| `ANN-6.7-008` | P2 | não iniciado | governança | 6.7 Conformidade | Common Criteria. |
| `ANN-7.1-001` | P0 | não iniciado | operação | 7.1 Observabilidade | OpenTelemetry de verdade. |
| `ANN-7.1-002` | P0 | não iniciado | operação | 7.1 Observabilidade | Export OTLP. |
| `ANN-7.1-003` | P0 | não iniciado | operação | 7.1 Observabilidade | Tracing distribuído. |
| `ANN-7.1-004` | P0 | não iniciado | operação | 7.1 Observabilidade | Correlação jobs↔tenants↔solver. |
| `ANN-7.1-005` | P1 | não iniciado | operação | 7.1 Observabilidade | Prometheus remoto. |
| `ANN-7.1-006` | P1 | não iniciado | operação | 7.1 Observabilidade | Loki para logs. |
| `ANN-7.1-007` | P1 | não iniciado | operação | 7.1 Observabilidade | Tempo para traces. |
| `ANN-7.1-008` | P1 | não iniciado | operação | 7.1 Observabilidade | Grafana com dashboards por tenant. |
| `ANN-7.1-009` | P2 | não iniciado | operação | 7.1 Observabilidade | Pyroscope para profiling. |
| `ANN-7.1-010` | P2 | não iniciado | operação | 7.1 Observabilidade | Parca para profiling contínuo. |
| `ANN-7.2-001` | P0 | não iniciado | operação | 7.2 SLO/SLI | Definir SLO 99.9%. |
| `ANN-7.2-002` | P0 | não iniciado | operação | 7.2 SLO/SLI | p95 < 2s para jobs simples. |
| `ANN-7.2-003` | P0 | não iniciado | operação | 7.2 SLO/SLI | p99 < 10s para jobs complexos. |
| `ANN-7.2-004` | P0 | não iniciado | operação | 7.2 SLO/SLI | Throughput 10k jobs/h por cluster. |
| `ANN-7.2-005` | P1 | não iniciado | operação | 7.2 SLO/SLI | Error budget. |
| `ANN-7.2-006` | P1 | não iniciado | operação | 7.2 SLO/SLI | Burn rate alerts. |
| `ANN-7.2-007` | P1 | não iniciado | operação | 7.2 SLO/SLI | SLO por tenant. |
| `ANN-7.2-008` | P2 | não iniciado | operação | 7.2 SLO/SLI | SLO por domínio. |
| `ANN-7.3-001` | P0 | implementado sem validação | operação | 7.3 Incidentes | Runbook completo. |
| `ANN-7.3-002` | P0 | não iniciado | operação | 7.3 Incidentes | On-call rotation. |
| `ANN-7.3-003` | P0 | não iniciado | operação | 7.3 Incidentes | PagerDuty/Opsgenie. |
| `ANN-7.3-004` | P1 | não iniciado | operação | 7.3 Incidentes | Post-mortems públicos. |
| `ANN-7.3-005` | P1 | não iniciado | operação | 7.3 Incidentes | Chaos engineering (Chaos Monkey, Litmus). |
| `ANN-7.3-006` | P1 | não iniciado | operação | 7.3 Incidentes | Game days. |
| `ANN-7.3-007` | P2 | não iniciado | operação | 7.3 Incidentes | Simulação de desastres. |
| `ANN-7.4-001` | P0 | implementado sem validação | operação | 7.4 Performance | Benchmark de throughput. |
| `ANN-7.4-002` | P0 | não iniciado | operação | 7.4 Performance | Benchmark de latência. |
| `ANN-7.4-003` | P0 | não iniciado | operação | 7.4 Performance | Profiling contínuo. |
| `ANN-7.4-004` | P1 | não iniciado | operação | 7.4 Performance | Otimização de queries. |
| `ANN-7.4-005` | P1 | não iniciado | operação | 7.4 Performance | Otimização de rede. |
| `ANN-7.4-006` | P1 | não iniciado | operação | 7.4 Performance | Otimização de solver. |
| `ANN-7.4-007` | P2 | não iniciado | operação | 7.4 Performance | Otimização de LLM (quantização, destilação). |
| `ANN-7.4-008` | P2 | não iniciado | operação | 7.4 Performance | Otimização de energia. |
| `ANN-7.5-001` | P0 | não iniciado | operação | 7.5 Custo | Custo por verificação < $0.01. |
| `ANN-7.5-002` | P0 | não iniciado | operação | 7.5 Custo | Custo por tenant. |
| `ANN-7.5-003` | P1 | não iniciado | operação | 7.5 Custo | Otimização de spot instances. |
| `ANN-7.5-004` | P1 | não iniciado | operação | 7.5 Custo | Otimização de storage. |
| `ANN-7.5-005` | P1 | não iniciado | operação | 7.5 Custo | Otimização de LLM. |
| `ANN-7.5-006` | P2 | não iniciado | operação | 7.5 Custo | Custo por domínio. |
| `ANN-7.5-007` | P2 | não iniciado | operação | 7.5 Custo | Custo por região. |
| `ANN-8.1-001` | P0 | não iniciado | produto | 8.1 Frontend | React/Next/Svelte com build. |
| `ANN-8.1-002` | P0 | não iniciado | produto | 8.1 Frontend | PWA offline. |
| `ANN-8.1-003` | P0 | implementado sem validação | produto | 8.1 Frontend | SSE/WebSocket para progresso. |
| `ANN-8.1-004` | P0 | não iniciado | produto | 8.1 Frontend | Drafts no servidor. |
| `ANN-8.1-005` | P1 | não iniciado | produto | 8.1 Frontend | Colaboração em tempo real (CRDT). |
| `ANN-8.1-006` | P1 | não iniciado | produto | 8.1 Frontend | Exportação para Overleaf. |
| `ANN-8.1-007` | P1 | não iniciado | produto | 8.1 Frontend | Exportação para Jupyter. |
| `ANN-8.1-008` | P1 | não iniciado | produto | 8.1 Frontend | Exportação para VS Code. |
| `ANN-8.1-009` | P1 | não iniciado | produto | 8.1 Frontend | Exportação para Lean/Coq. |
| `ANN-8.1-010` | P2 | não iniciado | produto | 8.1 Frontend | Editor visual de fórmulas. |
| `ANN-8.1-011` | P2 | não iniciado | produto | 8.1 Frontend | Editor visual de provas. |
| `ANN-8.1-012` | P2 | não iniciado | produto | 8.1 Frontend | Modo acessível (WCAG 2.2 AA). |
| `ANN-8.1-013` | P2 | não iniciado | produto | 8.1 Frontend | Internacionalização. |
| `ANN-8.2-001` | P0 | implementado sem validação | engenharia | 8.2 SDK e CLI | SDK Python. |
| `ANN-8.2-002` | P0 | não iniciado | engenharia | 8.2 SDK e CLI | SDK JavaScript/TypeScript. |
| `ANN-8.2-003` | P0 | implementado sem validação | engenharia | 8.2 SDK e CLI | CLI robusta. |
| `ANN-8.2-004` | P1 | não iniciado | engenharia | 8.2 SDK e CLI | SDK Rust. |
| `ANN-8.2-005` | P1 | não iniciado | engenharia | 8.2 SDK e CLI | SDK Go. |
| `ANN-8.2-006` | P1 | não iniciado | engenharia | 8.2 SDK e CLI | SDK Java. |
| `ANN-8.2-007` | P1 | não iniciado | engenharia | 8.2 SDK e CLI | GitHub Action. |
| `ANN-8.2-008` | P2 | não iniciado | engenharia | 8.2 SDK e CLI | GitLab CI. |
| `ANN-8.2-009` | P2 | não iniciado | engenharia | 8.2 SDK e CLI | Jenkins plugin. |
| `ANN-8.2-010` | P2 | não iniciado | engenharia | 8.2 SDK e CLI | VSCode extension. |
| `ANN-8.2-011` | P2 | não iniciado | engenharia | 8.2 SDK e CLI | Jupyter extension. |
| `ANN-8.2-012` | P2 | não iniciado | engenharia | 8.2 SDK e CLI | Overleaf plugin. |
| `ANN-8.3-001` | P0 | não iniciado | produto | 8.3 Integrações | GitHub. |
| `ANN-8.3-002` | P0 | não iniciado | produto | 8.3 Integrações | GitLab. |
| `ANN-8.3-003` | P0 | não iniciado | produto | 8.3 Integrações | Overleaf. |
| `ANN-8.3-004` | P1 | não iniciado | produto | 8.3 Integrações | Jupyter. |
| `ANN-8.3-005` | P1 | não iniciado | produto | 8.3 Integrações | VSCode. |
| `ANN-8.3-006` | P1 | não iniciado | produto | 8.3 Integrações | Slack. |
| `ANN-8.3-007` | P1 | não iniciado | produto | 8.3 Integrações | Discord. |
| `ANN-8.3-008` | P1 | não iniciado | produto | 8.3 Integrações | Notion. |
| `ANN-8.3-009` | P2 | não iniciado | produto | 8.3 Integrações | Confluence. |
| `ANN-8.3-010` | P2 | não iniciado | produto | 8.3 Integrações | Obsidian. |
| `ANN-8.3-011` | P2 | não iniciado | produto | 8.3 Integrações | Zotero. |
| `ANN-8.3-012` | P2 | não iniciado | produto | 8.3 Integrações | Mendeley. |
| `ANN-8.4-001` | P0 | validado | produto | 8.4 Documentação | Documentação de DSL. |
| `ANN-8.4-002` | P0 | implementado sem validação | produto | 8.4 Documentação | Documentação de API. |
| `ANN-8.4-003` | P0 | implementado sem validação | produto | 8.4 Documentação | Tutoriais. |
| `ANN-8.4-004` | P0 | validado | produto | 8.4 Documentação | Exemplos. |
| `ANN-8.4-005` | P1 | não iniciado | produto | 8.4 Documentação | Livro online (mdBook, Docusaurus). |
| `ANN-8.4-006` | P1 | não iniciado | produto | 8.4 Documentação | Vídeos. |
| `ANN-8.4-007` | P1 | não iniciado | produto | 8.4 Documentação | Cursos. |
| `ANN-8.4-008` | P2 | não iniciado | produto | 8.4 Documentação | Certificação de usuários. |
| `ANN-8.4-009` | P2 | não iniciado | produto | 8.4 Documentação | Tradução multi-idioma. |
| `ANN-9.1-001` | P0 | dependente de decisão | governança | 9.1 Open source | Licença clara. |
| `ANN-9.1-002` | P0 | validado | governança | 9.1 Open source | Contributing guide. |
| `ANN-9.1-003` | P0 | implementado sem validação | governança | 9.1 Open source | Code of conduct. |
| `ANN-9.1-004` | P0 | implementado sem validação | governança | 9.1 Open source | Issue templates. |
| `ANN-9.1-005` | P0 | implementado sem validação | governança | 9.1 Open source | PR templates. |
| `ANN-9.1-006` | P1 | não iniciado | governança | 9.1 Open source | RFC process. |
| `ANN-9.1-007` | P1 | implementado sem validação | governança | 9.1 Open source | Roadmap público. |
| `ANN-9.1-008` | P1 | não iniciado | governança | 9.1 Open source | Maintainers pagos. |
| `ANN-9.1-009` | P2 | não iniciado | governança | 9.1 Open source | Fundação sem fins lucrativos. |
| `ANN-9.1-010` | P2 | não iniciado | governança | 9.1 Open source | Conselho científico. |
| `ANN-9.2-001` | P0 | não iniciado | colaboração externa | 9.2 Ecossistema | Contribuições para Mathlib. |
| `ANN-9.2-002` | P0 | não iniciado | colaboração externa | 9.2 Ecossistema | Integração com LeanDojo. |
| `ANN-9.2-003` | P0 | não iniciado | colaboração externa | 9.2 Ecossistema | Integração com miniF2F. |
| `ANN-9.2-004` | P0 | não iniciado | colaboração externa | 9.2 Ecossistema | Integração com PutnamBench. |
| `ANN-9.2-005` | P1 | não iniciado | colaboração externa | 9.2 Ecossistema | Integração com ProofNet. |
| `ANN-9.2-006` | P1 | não iniciado | colaboração externa | 9.2 Ecossistema | Integração com Lean Workbook. |
| `ANN-9.2-007` | P1 | não iniciado | colaboração externa | 9.2 Ecossistema | Integração com SMT-LIB. |
| `ANN-9.2-008` | P1 | não iniciado | colaboração externa | 9.2 Ecossistema | Integração com TPTP. |
| `ANN-9.2-009` | P2 | não iniciado | colaboração externa | 9.2 Ecossistema | Integração com OpenMath. |
| `ANN-9.2-010` | P2 | não iniciado | colaboração externa | 9.2 Ecossistema | Integração com MathML. |
| `ANN-9.2-011` | P2 | não iniciado | colaboração externa | 9.2 Ecossistema | Integração com OMDoc. |
| `ANN-9.3-001` | P0 | bloqueado | colaboração externa | 9.3 Eventos | Workshop em ITP. |
| `ANN-9.3-002` | P0 | bloqueado | colaboração externa | 9.3 Eventos | Workshop em CPP. |
| `ANN-9.3-003` | P0 | bloqueado | colaboração externa | 9.3 Eventos | Workshop em CAV. |
| `ANN-9.3-004` | P1 | não iniciado | colaboração externa | 9.3 Eventos | Summer school. |
| `ANN-9.3-005` | P1 | não iniciado | colaboração externa | 9.3 Eventos | Hackathon. |
| `ANN-9.3-006` | P1 | não iniciado | colaboração externa | 9.3 Eventos | Competição anual. |
| `ANN-9.3-007` | P1 | não iniciado | colaboração externa | 9.3 Eventos | Conference própria (Verified Science). |
| `ANN-9.3-008` | P2 | não iniciado | colaboração externa | 9.3 Eventos | Meetups locais. |
| `ANN-9.3-009` | P2 | não iniciado | colaboração externa | 9.3 Eventos | Podcast. |
| `ANN-9.3-010` | P2 | não iniciado | colaboração externa | 9.3 Eventos | Newsletter. |
| `ANN-9.4-001` | P0 | não iniciado | colaboração externa | 9.4 Parcerias | MIT CSAIL. |
| `ANN-9.4-002` | P0 | não iniciado | colaboração externa | 9.4 Parcerias | Stanford CSLI. |
| `ANN-9.4-003` | P0 | não iniciado | colaboração externa | 9.4 Parcerias | CMU. |
| `ANN-9.4-004` | P0 | não iniciado | colaboração externa | 9.4 Parcerias | Berkeley. |
| `ANN-9.4-005` | P0 | não iniciado | colaboração externa | 9.4 Parcerias | Princeton IAS. |
| `ANN-9.4-006` | P1 | não iniciado | colaboração externa | 9.4 Parcerias | ETH Zurich. |
| `ANN-9.4-007` | P1 | não iniciado | colaboração externa | 9.4 Parcerias | EPFL. |
| `ANN-9.4-008` | P1 | não iniciado | colaboração externa | 9.4 Parcerias | INRIA. |
| `ANN-9.4-009` | P1 | não iniciado | colaboração externa | 9.4 Parcerias | Max Planck. |
| `ANN-9.4-010` | P1 | não iniciado | colaboração externa | 9.4 Parcerias | DeepMind. |
| `ANN-9.4-011` | P1 | não iniciado | colaboração externa | 9.4 Parcerias | Microsoft Research. |
| `ANN-9.4-012` | P1 | não iniciado | colaboração externa | 9.4 Parcerias | AI2. |
| `ANN-9.4-013` | P2 | não iniciado | colaboração externa | 9.4 Parcerias | OpenAI. |
| `ANN-9.4-014` | P2 | não iniciado | colaboração externa | 9.4 Parcerias | Anthropic. |
| `ANN-9.4-015` | P2 | não iniciado | colaboração externa | 9.4 Parcerias | NVIDIA. |
| `ANN-9.4-016` | P2 | não iniciado | colaboração externa | 9.4 Parcerias | Google Research. |
| `ANN-9.5-001` | P0 | não iniciado | produto | 9.5 Visibilidade | Blog técnico. |
| `ANN-9.5-002` | P0 | não iniciado | produto | 9.5 Visibilidade | Twitter/X ativo. |
| `ANN-9.5-003` | P0 | não iniciado | produto | 9.5 Visibilidade | LinkedIn. |
| `ANN-9.5-004` | P0 | não iniciado | produto | 9.5 Visibilidade | Mastodon. |
| `ANN-9.5-005` | P1 | não iniciado | produto | 9.5 Visibilidade | YouTube. |
| `ANN-9.5-006` | P1 | não iniciado | produto | 9.5 Visibilidade | Twitch (live coding). |
| `ANN-9.5-007` | P1 | não iniciado | produto | 9.5 Visibilidade | Reddit. |
| `ANN-9.5-008` | P1 | não iniciado | produto | 9.5 Visibilidade | Hacker News. |
| `ANN-9.5-009` | P2 | não iniciado | produto | 9.5 Visibilidade | TikTok. |
| `ANN-9.5-010` | P2 | não iniciado | produto | 9.5 Visibilidade | Instagram. |
| `ANN-10-001` | P0 | não iniciado | governança | 10. Governança | Estatuto da fundação. |
| `ANN-10-002` | P0 | não iniciado | governança | 10. Governança | Conselho de administração. |
| `ANN-10-003` | P0 | não iniciado | governança | 10. Governança | Conselho científico. |
| `ANN-10-004` | P0 | não iniciado | governança | 10. Governança | Conselho técnico. |
| `ANN-10-005` | P1 | não iniciado | governança | 10. Governança | Política de conflitos de interesse. |
| `ANN-10-006` | P1 | não iniciado | governança | 10. Governança | Política de transparência. |
| `ANN-10-007` | P1 | não iniciado | governança | 10. Governança | Política de privacidade. |
| `ANN-10-008` | P1 | não iniciado | governança | 10. Governança | Política de segurança. |
| `ANN-10-009` | P1 | não iniciado | governança | 10. Governança | Política de ética. |
| `ANN-10-010` | P2 | não iniciado | governança | 10. Governança | Política de diversidade e inclusão. |
| `ANN-10-011` | P2 | não iniciado | governança | 10. Governança | Política de sustentabilidade. |
| `ANN-10-012` | P2 | não iniciado | governança | 10. Governança | Política de responsabilidade social. |
| `ANN-11-001` | P0 | não iniciado | financiamento | 11. Funding | NSF. |
| `ANN-11-002` | P0 | não iniciado | financiamento | 11. Funding | ERC. |
| `ANN-11-003` | P0 | não iniciado | financiamento | 11. Funding | DARPA. |
| `ANN-11-004` | P0 | não iniciado | financiamento | 11. Funding | Simons Foundation. |
| `ANN-11-005` | P0 | não iniciado | financiamento | 11. Funding | Sloan Foundation. |
| `ANN-11-006` | P0 | não iniciado | financiamento | 11. Funding | Moore Foundation. |
| `ANN-11-007` | P0 | não iniciado | financiamento | 11. Funding | Schmidt Futures. |
| `ANN-11-008` | P0 | não iniciado | financiamento | 11. Funding | Chan Zuckerberg Initiative. |
| `ANN-11-009` | P1 | não iniciado | financiamento | 11. Funding | Wellcome Trust. |
| `ANN-11-010` | P1 | não iniciado | financiamento | 11. Funding | Templeton Foundation. |
| `ANN-11-011` | P1 | não iniciado | financiamento | 11. Funding | Alfred P. Sloan. |
| `ANN-11-012` | P1 | não iniciado | financiamento | 11. Funding | Packard Foundation. |
| `ANN-11-013` | P1 | não iniciado | financiamento | 11. Funding | NVIDIA grants. |
| `ANN-11-014` | P1 | não iniciado | financiamento | 11. Funding | Microsoft grants. |
| `ANN-11-015` | P1 | não iniciado | financiamento | 11. Funding | Google grants. |
| `ANN-11-016` | P1 | não iniciado | financiamento | 11. Funding | Amazon grants. |
| `ANN-11-017` | P2 | não iniciado | financiamento | 11. Funding | Meta grants. |
| `ANN-11-018` | P2 | não iniciado | financiamento | 11. Funding | OpenAI grants. |
| `ANN-11-019` | P2 | não iniciado | financiamento | 11. Funding | Anthropic grants. |
| `ANN-11-020` | P2 | não iniciado | financiamento | 11. Funding | DeepMind grants. |
| `ANN-11-021` | P2 | não iniciado | financiamento | 11. Funding | Cloud credits (AWS, GCP, Azure). |
| `ANN-11-022` | P2 | não iniciado | financiamento | 11. Funding | HPC allocations (XSEDE, PRACE). |
| `ANN-12-001` | P0 | bloqueado | colaboração externa | 12. Educação e talento | Programa de PhD afiliado. |
| `ANN-12-002` | P0 | não iniciado | colaboração externa | 12. Educação e talento | Pós-docs financiados. |
| `ANN-12-003` | P0 | não iniciado | colaboração externa | 12. Educação e talento | Summer school. |
| `ANN-12-004` | P1 | não iniciado | colaboração externa | 12. Educação e talento | Cursos abertos. |
| `ANN-12-005` | P1 | não iniciado | colaboração externa | 12. Educação e talento | Mentoria para América Latina. |
| `ANN-12-006` | P1 | não iniciado | colaboração externa | 12. Educação e talento | Mentoria para África. |
| `ANN-12-007` | P1 | não iniciado | colaboração externa | 12. Educação e talento | Mentoria para Ásia. |
| `ANN-12-008` | P1 | não iniciado | colaboração externa | 12. Educação e talento | Hackathons. |
| `ANN-12-009` | P2 | não iniciado | colaboração externa | 12. Educação e talento | Competições estudantis. |
| `ANN-12-010` | P2 | não iniciado | colaboração externa | 12. Educação e talento | Bolsas para minorias. |
| `ANN-12-011` | P2 | não iniciado | colaboração externa | 12. Educação e talento | Programa de residência. |
| `ANN-12-012` | P2 | não iniciado | colaboração externa | 12. Educação e talento | Co-supervisão de teses. |
| `ANN-13-001` | P0 | não iniciado | governança | 13. Ética, política e sociedade | Política de uso responsável. |
| `ANN-13-002` | P0 | não iniciado | governança | 13. Ética, política e sociedade | Política anti-desinformação. |
| `ANN-13-003` | P0 | não iniciado | governança | 13. Ética, política e sociedade | Política de privacidade. |
| `ANN-13-004` | P0 | não iniciado | governança | 13. Ética, política e sociedade | Política de segurança. |
| `ANN-13-005` | P1 | não iniciado | governança | 13. Ética, política e sociedade | Auditoria de viés. |
| `ANN-13-006` | P1 | não iniciado | governança | 13. Ética, política e sociedade | Auditoria de equidade. |
| `ANN-13-007` | P1 | não iniciado | governança | 13. Ética, política e sociedade | Auditoria de impacto social. |
| `ANN-13-008` | P1 | não iniciado | governança | 13. Ética, política e sociedade | Publicação de resultados negativos. |
| `ANN-13-009` | P2 | não iniciado | governança | 13. Ética, política e sociedade | Conselho de ética. |
| `ANN-13-010` | P2 | não iniciado | governança | 13. Ética, política e sociedade | Engajamento com policymakers. |
| `ANN-13-011` | P2 | não iniciado | governança | 13. Ética, política e sociedade | Engajamento com sociedade civil. |
| `ANN-13-012` | P2 | não iniciado | governança | 13. Ética, política e sociedade | Relatório anual de impacto. |
| `ANN-14-001` | P0 | não iniciado | produto | 14. Métricas de sucesso 10/10 | 10+ papers em CAV/ITP/CPP/TACAS/NeurIPS/ICML. |
| `ANN-14-002` | P0 | não iniciado | produto | 14. Métricas de sucesso 10/10 | 100+ citações por paper principal. |
| `ANN-14-003` | P0 | não iniciado | produto | 14. Métricas de sucesso 10/10 | Benchmark adotado por 50+ grupos. |
| `ANN-14-004` | P0 | não iniciado | produto | 14. Métricas de sucesso 10/10 | 100+ contribuições para Mathlib. |
| `ANN-14-005` | P0 | não iniciado | produto | 14. Métricas de sucesso 10/10 | Certificação independente de 100% dos aceites críticos. |
| `ANN-14-006` | P0 | não iniciado | produto | 14. Métricas de sucesso 10/10 | Custo por verificação < $0.01. |
| `ANN-14-007` | P0 | não iniciado | produto | 14. Métricas de sucesso 10/10 | SLO 99.9% medido. |
| `ANN-14-008` | P0 | não iniciado | produto | 14. Métricas de sucesso 10/10 | 10k jobs/h por cluster medido. |
| `ANN-14-009` | P1 | não iniciado | produto | 14. Métricas de sucesso 10/10 | 100+ alunos formados. |
| `ANN-14-010` | P1 | não iniciado | produto | 14. Métricas de sucesso 10/10 | 50+ alunos em MIT/Stanford/CMU/ETH. |
| `ANN-14-011` | P1 | não iniciado | produto | 14. Métricas de sucesso 10/10 | $10M+ em grants. |
| `ANN-14-012` | P1 | não iniciado | produto | 14. Métricas de sucesso 10/10 | 10+ parcerias com instituições top. |
| `ANN-14-013` | P2 | não iniciado | produto | 14. Métricas de sucesso 10/10 | 1M+ usuários. |
| `ANN-14-014` | P2 | não iniciado | produto | 14. Métricas de sucesso 10/10 | 100+ empresas usando. |
| `ANN-14-015` | P2 | não iniciado | produto | 14. Métricas de sucesso 10/10 | 10+ prêmios. |
| `ANN-14-016` | P2 | não iniciado | produto | 14. Métricas de sucesso 10/10 | 1+ teorema formalizado que resolve problema aberto. |
| `ANN-15-001` | P0 | não iniciado | governança | 15. Riscos e mitigação | Alucinação de LLM → verifier-in-the-loop. |
| `ANN-15-002` | P0 | não iniciado | governança | 15. Riscos e mitigação | Bugs de solver → certificados independentes. |
| `ANN-15-003` | P0 | não iniciado | governança | 15. Riscos e mitigação | TCB grande → kernel mínimo verificado. |
| `ANN-15-004` | P0 | não iniciado | governança | 15. Riscos e mitigação | Explosão combinatória → portfolio + cube-and-conquer. |
| `ANN-15-005` | P0 | não iniciado | governança | 15. Riscos e mitigação | Segurança de execução → sandbox gVisor/Firecracker. |
| `ANN-15-006` | P0 | não iniciado | governança | 15. Riscos e mitigação | Custo de GPU/LLM → quantização + destilação + spot. |
| `ANN-15-007` | P0 | não iniciado | governança | 15. Riscos e mitigação | Overfitting no benchmark → hidden sets. |
| `ANN-15-008` | P1 | não iniciado | governança | 15. Riscos e mitigação | Dependência de fornecedor → multi-cloud. |
| `ANN-15-009` | P1 | não iniciado | governança | 15. Riscos e mitigação | Perda de talento → cultura + compensação. |
| `ANN-15-010` | P1 | não iniciado | governança | 15. Riscos e mitigação | Falta de funding → diversificação. |
| `ANN-15-011` | P2 | não iniciado | governança | 15. Riscos e mitigação | Regulação → conformidade proativa. |
| `ANN-15-012` | P2 | não iniciado | governança | 15. Riscos e mitigação | Geopolítica → neutralidade + multi-região. |
| `ANN-16-001` | P0 | não iniciado | governança | Meses 1–3 | Kernel externo (Lean/Coq). |
| `ANN-16-002` | P0 | não iniciado | governança | Meses 1–3 | Alethe/LFSC. |
| `ANN-16-003` | P0 | não iniciado | governança | Meses 1–3 | Postgres + NATS reais. |
| `ANN-16-004` | P0 | não iniciado | governança | Meses 1–3 | OTLP. |
| `ANN-16-005` | P0 | não iniciado | governança | Meses 1–3 | Paper 1 submetido. |
| `ANN-16-006` | P0 | não iniciado | governança | Meses 4–6 | Autoformalização v1. |
| `ANN-16-007` | P0 | não iniciado | governança | Meses 4–6 | PhysVerifyBench 10k. |
| `ANN-16-008` | P0 | não iniciado | governança | Meses 4–6 | OIDC + RBAC. |
| `ANN-16-009` | P0 | não iniciado | governança | Meses 4–6 | Sandbox gVisor. |
| `ANN-16-010` | P0 | não iniciado | governança | Meses 4–6 | Paper 2 submetido. |
| `ANN-16-011` | P0 | não iniciado | governança | Meses 7–12 | Autoformalização v2. |
| `ANN-16-012` | P0 | não iniciado | governança | Meses 7–12 | PhysVerifyBench 100k. |
| `ANN-16-013` | P0 | não iniciado | governança | Meses 7–12 | K8s produção. |
| `ANN-16-014` | P0 | não iniciado | governança | Meses 7–12 | Multi-tenant real. |
| `ANN-16-015` | P0 | não iniciado | governança | Meses 7–12 | Papers 3–5 submetidos. |
| `ANN-16-016` | P0 | não iniciado | governança | Meses 7–12 | Fundação criada. |
| `ANN-16-017` | P0 | não iniciado | governança | Meses 7–12 | Primeiro grant. |
| `ANN-16-018` | P0 | não iniciado | governança | Meses 13–24 | Leaderboard global. |
| `ANN-16-019` | P0 | não iniciado | governança | Meses 13–24 | Competição anual. |
| `ANN-16-020` | P0 | não iniciado | governança | Meses 13–24 | Summer school. |
| `ANN-16-021` | P0 | não iniciado | governança | Meses 13–24 | Parcerias MIT/Stanford/CMU. |
| `ANN-16-022` | P0 | não iniciado | governança | Meses 13–24 | Papers 6–10. |
| `ANN-16-023` | P0 | não iniciado | governança | Meses 13–24 | $1M+ em grants. |
| `ANN-16-024` | P0 | não iniciado | governança | Meses 13–24 | 10+ alunos formados. |
| `ANN-16-025` | P0 | não iniciado | governança | Meses 25–60 | Campo consolidado. |
| `ANN-16-026` | P0 | não iniciado | governança | Meses 25–60 | 100+ papers. |
| `ANN-16-027` | P0 | não iniciado | governança | Meses 25–60 | 1M+ usuários. |
| `ANN-16-028` | P0 | não iniciado | governança | Meses 25–60 | $10M+ em grants. |
| `ANN-16-029` | P0 | não iniciado | governança | Meses 25–60 | Prêmios. |
| `ANN-16-030` | P0 | não iniciado | governança | Meses 25–60 | Impacto global. |
| `PARA-PILLAR-01` | P0 | não iniciado | pesquisa | Resumo brutal | Certificação independente (Lean/Coq/Alethe). |
| `PARA-PILLAR-02` | P0 | não iniciado | pesquisa | Resumo brutal | Autoformalização verificada (LLM + verifier-in-the-loop). |
| `PARA-PILLAR-03` | P0 | não iniciado | pesquisa | Resumo brutal | Benchmark global (100k+ com leaderboard). |
| `PARA-PILLAR-04` | P0 | não iniciado | pesquisa | Resumo brutal | Arquitetura distribuída real (Postgres + NATS + S3 + K8s). |
| `PARA-PILLAR-05` | P0 | implementado sem validação | pesquisa | Resumo brutal | Multi-tenant e segurança (OIDC + RBAC + sandbox). |
| `PARA-PILLAR-06` | P0 | não iniciado | pesquisa | Resumo brutal | Papers e teoria (CAV/ITP/CPP/NeurIPS). |
| `PARA-PILLAR-07` | P0 | não iniciado | pesquisa | Resumo brutal | Comunidade e governança (Mathlib + fundação + conselho). |
| `PARA-PILLAR-08` | P0 | não iniciado | pesquisa | Resumo brutal | Funding e talento (NSF/ERC + PhDs + pós-docs). |
| `PARA-SCORES-01` | P3 | não aplicável | pesquisa | Resumo brutal | O README já está em 9/10. O código, em 6/10. A ciência, em 2/10. A comunidade, em 1/10. A governança, em 0/10. O funding, em 0/10. |
| `PARA-SCORES-02` | P3 | não aplicável | pesquisa | Resumo brutal | A média é 3/10. |
| `PARA-FALLBACK-01` | P0 | não aplicável | pesquisa | Resumo brutal | Se faltar um dos oito pilares, 7/10; dois, 5/10; três, projeto local bem-feito. |

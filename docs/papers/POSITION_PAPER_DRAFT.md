# Rascunho de position paper — não submetido

**Status:** rascunho interno. Não é artigo aceito, preprint publicado, nem evidência de originalidade. Nenhuma venue foi contactada.

**Tese em uma frase (anexo):** verificação formal certificada e automatizada de conhecimento científico em escala.

**Nome do campo (decisão em aberto):** *Verified Science* **ou** *Formal Scientific Computing*. Este rascunho usa “Verified Science” apenas como rótulo de trabalho.

## 1. O problema

Modelos de linguagem produzem física e matemática fluentes e erradas. Assistentes de prova e solvers oferecem garantias estreitas, mas não leem artigos livres. O intervalo entre o texto científico e uma obrigação checável é hoje artesanal, opaco e fácil de superinterpretar.

NatalIA, neste repositório, verifica **formalizações declaradas** numa DSL pequena. Não verifica LaTeX livre, não prova fidelidade documento↔formalização e não estabelece validade empírica.

## 2. Escopo negativo

O sistema **não** faz, até haver evidência em contrário:

1. Tradução fiel de artigos, livros ou PDFs para a DSL.
2. Aceite SMT como certificado independente.
3. Promoção de exportação Lean com `sorry`, comentários ou toolchain ausente a `KERNEL_CHECKED`.
4. Julgamento de teorias físicas contra experimento.
5. Conformidade LGPD/SOC2/SLSA apenas por menção em documentação.

## 3. Problemas abertos (agenda, não resultados)

1. Qual fragmento de afirmações científicas admite certificado independente com TCB auditável?
2. Como recusar formalizações infiéis mesmo quando a obrigação errada é demonstrável?
3. Como medir FPR populacional com ground truth independente e intervalos, não com zero erros numa amostra pequena?
4. Que modelo de confiança separa autoria criptográfica, checagem de kernel e verdade empírica?
5. Como operar verificação multi-tenant sem vazar artefatos por cache, fila ou tempo de resposta?

Cada pergunta exige hipótese falsificável, baseline e ameaças à validade. Ver `docs/RESEARCH_HYPOTHESES.md`.

## 4. Verticais

Iniciais (anexo): matemática pura, física teórica, engenharia/controle.

Futuras (anexo): finanças quantitativas, química computacional, biologia de sistemas.

A implementação local atual cobre sobretudo identidades polinomiais e aritmética real de dimensão SI, não essas verticais como disciplinas.

## 5. Agenda de dez anos (aspiracional)

Preserva o cronograma do anexo (meses 1–60) como cenário, não como plano financiado. Dependências externas: kernel/checkers, corpora licenciados, instituições, grants e pessoas. Um agente de código não submete papers, não contrata auditoria e não cria fundação.

## 6. Contribuição pretendida (ainda não demonstrada)

Um laboratório reproduzível no qual **estado do job**, **conclusão** e **nível de garantia** são campos distintos; um fragmento polinomial com rechecagem independente; e uma matriz que impede que o README avance além do código.

## Referências a verificar

Venues citadas no anexo (CAV, TACAS, ITP, CPP, NeurIPS, JAR) e ferramentas (Lean 4, Z3, Alethe, Carcara) devem ser confirmadas nas versões vigentes antes de qualquer submissão. Este rascunho não contém teoremas novos.

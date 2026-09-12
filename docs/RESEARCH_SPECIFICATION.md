Aqui está a explicação exaustiva, **fim a fim (*****end-to-end*****)**, do **NatalIA**: desde a fundamentação conceitual e a formalização matemática até o pipeline de dados, execução em tempo de inferência, algoritmos de treino e o protocolo de validação para o paper.

# 1. Tese Central e Posicionamento Epistêmico

### O Problema Central

Grandes Modelos de Linguagem (LLMs) geram argumentos matemáticos e físicos com altíssima fluência textual, mas são propensos a **alucinações analíticas catastróficas**:

- Aceitam derivações com erros dimensionais sutis escondidos em constantes implícitas.



- Extrapolam limites assintóticos de forma inválida ($x \to \infty, \hbar \to 0$).



- Pulam lemas críticos de convergência (*proof holes*).



- Sofrem de *sycophancy* (viés de concordância com o usuário).




Por outro lado, provadores interativos de teoremas (ITPs como Lean 4) e solucionadores formais (SMT solvers como Z3, CAS como SymPy) oferecem garantias matemáticas estritas, mas **não conseguem ingerir rascunhos informais** (rabiscos de quadro, LaTeX informal, notas com notação abusiva).

### A Tese

> **NatalIA** é um agente neuro-simbólico que resolve o gap entre a intuição informal e o rigor computacional. Ele atua sob um **POMDP (Processo de Decisão Markoviano Parcialmente Observável)**, traduzindo sketches informais para uma **Linguagem Específica de Domínio (DSL) tipada**, sintetizando **obrigações de prova**, despachando-as para um **conjunto hierárquico de oráculos determinísticos**, e emitindo um veredito terminal acompanhado de **abstenção calibrada** e **garantias condicionais de validade e refutação**.
>
>
>

# 2. Arquitetura da DSL e Teoria de Tipos ($\mathcal{F}\_{\text{DSL}}$)

A DSL não é texto livre nem código Python arbitrário; é uma representação intermediária formal projetada para física teórica e matemática aplicada.

```
                  ┌─────────────────────────────────────────┐
                  │       Esboço Informal x (LaTeX)         │
                  └────────────────────┬────────────────────┘
                                       │ Tradução Neural (ϕ_θ)
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │       AST Tipada da DSL (NatalIA)        │
                  │  ├─ Dimensões: Grupo Abeliano ℚ⁷        │
                  │  ├─ Limites: Corpo de Hardy H_E         │
                  │  └─ Invariantes: Formas Diferenciais    │
                  └────────────────────┬────────────────────┘
                                       │ Compilação Determinística
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │  Obrigações de Prova: O = {o_dim, ...}  │
                  └─────────────────────────────────────────┘

```

### 2.1. Álgebra Dimensional em $\mathbb{Q}^7$

Cada termo $e$ instanciado na DSL carrega um tipo dimensional graduado sobre as 7 grandezas fundamentais do SI $[M, L, T, I, \Theta, N, J]$:

$$\mathbf{d}(e) = [d\_1, d\_2, d\_3, d\_4, d\_5, d\_6, d\_7]^\top \in \mathbb{Q}^7$$

- **Operações Válidas:**



  - Soma/Subtração ($e\_1 \pm e\_2$): Exige $\mathbf{d}(e\_1) = \mathbf{d}(e\_2)$ (homogeneidade dimensional).



  - Multiplicação ($e\_1 \cdot e\_2$): $\mathbf{d}(e\_1 \cdot e\_2) = \mathbf{d}(e\_1) + \mathbf{d}(e\_2)$.



  - Potenciação ($e^\alpha$ com $\alpha \in \mathbb{Q}$): $\mathbf{d}(e^\alpha) = \alpha \cdot \mathbf{d}(e)$.



  - Funções Transcendentais ($\exp(e), \sin(e), \log(e)$): Exigem $\mathbf{d}(e) = \mathbf{0}$.



- **Unidades Naturais:** O compilador suporta projeções de calibre. Exemplo: em unidades de Planck ($c = \hbar = G = 1$), o espaço $\mathbb{Q}^7$ é projetado sobre potências de massa $\mathbb{Q}^1$ via transformações de matrizes de posto reduzido.




### 2.2. Fragmento Assintótico Decidível ($\mathcal{H}\_E$)

Para evitar a indecidibilidade geral da teoria de funções reais transcendentais, as regras de limite são restritas a um **Corpo de Hardy germinal $\mathcal{H}\_E$**:

- Fecho gerado por $\mathbb{R}(x)$, fechado sob composição finita de $\exp(\cdot)$ e $\log(\cdot)$ em domínios assintóticos reais ($x > x\_0$).



- Todo elemento $f \in \mathcal{H}\_E$ é eventualmente contínuo, diferenciável e monotônico, garantindo que o limite $\lim\_{x \to \infty} f(x)$ existe no conjunto $\mathbb{R} \cup \\{-\infty, +\infty\\}$.



- Se uma asserção informal contiver comportamentos intrinsecamente oscilatórios na fronteira (ex.: $\sin(1/x)$ quando $x \to 0$), o type-checker classifica o termo como **fora do fragmento**, retornando $\bot$ por construção antes de gastar recursos de computação.




# 3. Formulação Formal do POMDP

O processo de raciocínio, verificação e decisão não é uma chamada única de API; é formulado formalmente como um POMDP: $\mathcal{M} = \langle \mathcal{S}, \mathcal{A}, \mathcal{T}, \mathcal{R}, \Omega, \mathcal{O}\_{\text{obs}}, \gamma \rangle$.

### 3.1. Espaço de Estados Latentes ($\mathcal{S}$)

$$s = (x^\*, F^\*, \mathcal{O}^\*, \mathbf{y}^\*)$$

- $x^\*$: A intenção conceitual formal do cientista (inalcançável diretamente).



- $F^\*$: A especificação ground-truth correspondente na DSL.



- $\mathcal{O}^\*$: O conjunto completo de obrigações de prova latentes.



- $\mathbf{y}^\* \in \\{\text{Valid}, \text{Refuted}, \text{Undecided}\\}$: O status epistemológico objetivo da conjectura.




### 3.2. Espaço de Observações ($\Omega$)

A cada passo de decisão $t$, o modelo tem acesso ao histórico observado:

$$o\_t = \left( x, F\_{1\:t}, \mathcal{O}\_{1\:t}, \mathcal{H}\_t, \mathbf{c}\_{1\:t} \right)$$

- $x$: O rascunho textual/LaTeX de entrada.



- $F\_{1\:t}$: O programa parcial/completo construído na DSL.



- $\mathcal{O}\_{1\:t}$: As obrigações de prova extraídas deterministicamente até o momento:




  $$\mathcal{O} = \mathcal{O}\_{\text{dim}} \cup \mathcal{O}\_{\text{asymp}} \cup \mathcal{O}\_{\text{inv}}$$
- $\mathcal{H}\_t = \\{(o\_i, v\_k, r\_{i,k})\\}\_{i,k}$: O histórico de consultas aos oráculos, onde $r\_{i,k} \in \\{\text{Certified } (C), \text{Refuted } (R), \text{Unknown } (\bot)\\}$ é o resultado do oráculo $v\_k$ sobre a obrigação $o\_i$.



- $\mathbf{c}\_{1\:t} \in \mathbb{R}^+$: O custo cumulativo de latência e processamento computacional.




### 3.3. Espaço de Ações ($\mathcal{A}$)

O agente escolhe dinamicamente entre ações generativas, computacionais e terminais:

1. **$\text{Synthesize}(w)$**: Emite blocos de especificação na DSL $\mathcal{F}\_{\text{DSL}}$.



2. **$\text{Compile}$**: Aciona o compilador formal para extrair $\mathcal{O}(F)$. Se a DSL tiver erro de sintaxe ou tipos primitivos, retorna erro imediato no ambiente.



3. **$\text{Dispatch}(o\_i, v\_k)$**: Submete a obrigação $o\_i$ ao oráculo específico $v\_k$.



4. **$\text{Terminate}(y, \hat{p})$**: Emite o veredito final $y \in \\{\text{Accept}, \text{Refute}, \text{Abstain}\\}$ acompanhado da probabilidade de calibração $\hat{p} \in [0, 1]$.




# 4. Orquestração e Modelo de Confiança dos Oráculos

Quando uma obrigação $o\_i$ é despachada, ela é processada por um pool heterogêneo de motores simbólicos estruturados em uma hierarquia estrita de confiança (*Trust Hierarchy*):

```
                     ┌────────────────────────────────────┐
                     │     Obrigação de Prova o_i         │
                     └─────────────────┬──────────────────┘
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        ▼                              ▼                              ▼
 ┌──────────────┐               ┌──────────────┐               ┌──────────────┐
 │    Tier 1    │               │    Tier 2    │               │    Tier 3    │
 │  Lean 4 ITP  │               │ Z3 SMT / CAS │               │ Aritmética   │
 │   Kernel     │               │  Simbolismo  │               │  Intervalar  │
 └──────┬───────┘               └──────┬───────┘               └──────┬───────┘
        │                              │                              │
        │ Prova Estrita                │ Simplificação                │ Busca de
        │ C ou ⊥                       │ C, R ou ⊥                    │ Contraexemplo
        │                              │                              │ R ou ⊥
        └──────────────────────────────┼──────────────────────────────┘
                                       ▼
                       ┌───────────────────────────────┐
                       │ Árbitro de Confiança Epistêmica│
                       │     (Resolução de Conflitos)  │
                       └───────────────────────────────┘

```

### 4.1. Oráculos Disponíveis

- **$v\_{\text{ITP}}$ (Lean 4 / PhysLean):** O padrão de ouro. Tenta fechar as obrigações usando táticas automáticas (`aesop`, `ring`, `linarith`). Não alucina; se atesta $C$, a prova é matematicamente válida na base axiomática. Retorna $\bot$ se as táticas esgotarem o orçamento de passos.



- **$v\_{\text{SMT}}$ (Z3):** Codifica desigualdades dimensionais e restrições algébricas sobre reais como problemas de lógica de primeira ordem (teoria QF\_NRA - *Quantifier-Free Nonlinear Real Arithmetic*).



- **$v\_{\text{CAS}}$ (SymPy / SageMath):** Executa simplificações algébricas, cálculo de séries de Puiseux e expansões de Taylor/Laurent em $\mathcal{H}\_E$.



- **$v\_{\text{Interval}}$ (Aritmética Intervalar de Rigor Estrito):** Discretiza o espaço de parâmetros livres $\mathbf{p} \in \mathcal{P}$ em caixas intervalares e avalia bounds com aritmética de ponto flutuante com arredondamento controlado (via bibliotecas MPFI/Arb). Se encontrar uma região onde a asserção é estritamente violada ($f(\mathbf{p}\_0) < 0$ com limite superior do intervalo $< 0$), emite um **contraexemplo construtivo**.




### 4.2. Regras de Resolução de Conflitos

Se diferentes oráculos divergirem:

1. **Prioridade de Veto:** Provas de $v\_{\text{ITP}}$ sobrepõem qualquer simplificação heurística de $v\_{\text{CAS}}$.



2. **Prioridade de Contraexemplo:** Se $v\_{\text{Interval}}$ ou $v\_{\text{SMT}}$ apresentarem uma atribuição numérica concreta que falsifique uma desigualdade, o claim é classificado como **Refutado ($R$)**, a menos que o contraexemplo viole premissas de domínio.



3. **Curto-Circuito sob Indecisão:** Se $v\_{\text{CAS}}$ alegar validade, mas $v\_{\text{SMT}}$ acusar inconsistência sem contraexemplo explícito, a obrigação colapsa para **$\bot$ (Indecidível)**.




# 5. Pipeline End-to-End em Tempo de Execução

Aqui está o fluxo completo, passo a passo, percorrido por uma submissão de usuário:

```
[Entrada: LaTeX]
       │
       ▼
[Passo 1: Parsing e Tradução Neural ϕ_θ]
       │
       ▼
[Passo 2: Verificação Estática de Tipos (AST na DSL)] ──> [Erro de Tipo?] ──> Retorna Falha
       │                                                                        Imediata
       ▼
[Passo 3: Extração de Obrigações O = {o_dim, o_asymp, o_inv}]
       │
       ▼
[Passo 4: Loop POMDP com Políticas de Despacho]
       │  ├─ Submete o_dim -> Z3
       │  ├─ Submete o_asymp -> SymPy (em H_E)
       │  └─ Submete o_inv -> Lean 4
       │
       ▼
[Passo 5: Agregação de Resultados dos Oráculos]
       │
       ├─ Algum oráculo gerou contraexemplo válido? ──> [EMITIR VEREDITO: REFUTED]
       │                                                 (Retorna o contraexemplo exato)
       │
       ├─ Todas as obrigações foram certificadas (C)? ─> [EMITIR VEREDITO: ACCEPTED]
       │                                                 (Retorna certificado condicional)
       │
       └─ Restaram obrigações com veredito ⊥?
              │
              ▼
       [Passo 6: Módulo de Abstenção Calibrada]
              │
              ├─ Risco computacional/epistêmico elevado ──> [EMITIR VEREDITO: ABSTAIN]
              │                                             (Mapeia os proof-holes abertos)
              │
              └─ Confiança heurística insuficiente ─────> [EMITIR VEREDITO: UNKNOWN]

```

### Detalhamento dos Passos

1. **Ingestão e Parsing:** O pesquisador envia uma dedução em LaTeX. O módulo $\phi\_\theta$ (um transformer condicional ajustado) gera a estrutura intermediária na DSL.



2. **Type-Checking:** O compilador determinístico verifica a sintaxe e a compatibilidade das unidades fundamentais em $\mathbb{Q}^7$. Se uma equação tentar somar energia cinética com momento linear sem fatores de velocidade correspondentes, o processo é abortado imediatamente com erro de compilação sem gastar chamadas caras de solvers.



3. **Extração das Obrigações:** O compilador divide as asserções em lemas formais isolados ($\mathcal{O}$).



4. **Execução das Ações de Roteamento:** A política $\pi\_\theta(a\_t \mid o\_t)$ seleciona os oráculos mais eficientes para cada lema com base no histórico de observações e custo de tempo de máquina.



5. **Avaliação dos Resultados:**



   - Se um contraexemplo for isolado, o pipeline interrompe a busca e formula a refutação com o ponto exato de falha (exemplo: *"A conjetura falha para regimes ultra-relativísticos onde $v/c > 1 - 10^{-5}$"*).



   - Se todos os lemas receberem $C$, o sistema atesta validade formal.



6. **Decisão sob Incerteza:** Se o pool de oráculos retornar $\bot$ para uma ou mais obrigações (comum em equações diferenciais altamente não-lineares), o modelo ativa o estimador de calibração para decidir entre arriscar um veredito heurístico ou acionar **Abstenção ($u = 1$)**.




# 6. Aprendizado por Reforço com Verificador (RLVR) e Função de Custo

O modelo não aprende via imitação cega de texto. A política $\pi\_\theta$ é treinada via RL com feedback direto do ambiente simbólico (usando algoritmos de gradiente de política como PPO ou REINFORCE com baseline de valor).

### 6.1. Decomposição da Função de Recompensa

A recompensa terminal de um episódio é composta por três termos:

$$\mathcal{R}\_{\text{total}} = \mathcal{R}\_{\text{decision}}(y, \mathbf{y}^\*) - \lambda \sum\_{t=1}^T \text{Cost}(a\_t) - \eta \cdot \text{BrierScore}(\hat{p}, y)$$

Onde:

#### A Matriz de Decisão Assimétrica ($\mathcal{R}\_{\text{decision}}$)

O treinamento do NatalIA é penalizado com rigor extremo para qualquer **Falso Positivo**:

$$\mathcal{R}\_{\text{decision}}(y, \mathbf{y}^\*) = \begin{cases} +1.0 & \text{se } y = \text{Accept} \land \mathbf{y}^\* = \text{Valid} \\\ +0.8 & \text{se } y = \text{Refute} \land \mathbf{y}^\* = \text{Refuted} \text{ (com contraexemplo)} \\\ -\beta\_{\text{FA}} & \text{se } y = \text{Accept} \land \mathbf{y}^\* \neq \text{Valid} \quad (\beta\_{\text{FA}} \ge 20.0) \\\ -\beta\_{\text{FR}} & \text{se } y = \text{Refute} \land \mathbf{y}^\* = \text{Valid} \quad (\beta\_{\text{FR}} \ge 10.0) \\\ -c\_{\text{abst}} & \text{se } y = \text{Abstain} \quad (0 < c\_{\text{abst}} \ll \beta\_{\text{FA}}) \end{cases}$$

- **Por que essa assimetria é vital?** Em ciência, certificar um resultado falso ($\beta\_{\text{FA}}$) polui a literatura e invalida trabalhos subsequentes. O modelo precisa internalizar que **abster-se $(-c\_{\text{abst}})$ é ordens de grandeza preferível a alucinar uma prova falsa**.




#### O Custo Computacional ($\text{Cost}(a\_t)$)

Cada ação consome recursos reais:

- Chamar $v\_{\text{ITP}}$ tem custo de computação e latência alto.



- Chamar $v\_{\text{CAS}}$ tem custo baixo.



- O termo $-\lambda \sum \text{Cost}(a\_t)$ força a política a aprender **roteamento inteligente**: resolver trivialidades dimensionais via SMT barato antes de invocar provas caras em Lean 4.




#### A Calibração de Confiança (Brier Score)

$$\text{BrierScore}(\hat{p}, y) = (\hat{p} - \mathbb{I}[y = \mathbf{y}^\*])^2$$

Obriga a probabilidade emitida $\hat{p}$ a refletir a frequência estatística real de acerto do modelo, eliminando a típica superconfiança dos LLMs convencionais.

# 7. As Garantias Formais: Soundness Condicional

O paper sustenta duas garantias teóricas que delimitam rigorosamente o escopo de confiança do NatalIA:

### Teorema 1 (Soundness Relativo à Formalização)

> Seja $x$ o rascunho de entrada e $F = \phi\_\theta(x)$ o termo sintetizado na DSL. Se o verificador atestar $\bigwedge\_{i} v(o\_i) = C$, a validade matemática da representação $F$ é estritamente garantida pela base axiomática do kernel formal. A validade do rascunho original $x$ ocorre sob a condição necessária e suficiente de que o predicado semântico de refinamento se sustente:
>
>
>
>
> $$\text{Refines}(F, x) \equiv \text{True}$$

- **Implicação:** O sistema explicita ao usuário que o kernel garante $F$, isolando o componente neural $\phi\_\theta$ como a única fonte possível de desvio semântico.




### Teorema 2 (Falsificação por Contraexemplo Construtivo)

> Seja uma conjectura formal $F$. Se o oráculo de aritmética intervalar $v\_{\text{Interval}}$ encontrar uma atribuição concreta de parâmetros livres $\mathbf{p}\_0 \in \mathcal{P}$ e um raio de vizinhança $\epsilon > 0$ tais que:
>
>
>
>
> $$\inf\_{\mathbf{p} \in \mathcal{B}\_\epsilon(\mathbf{p}\_0)} \text{Violates}(F, \mathbf{p}) > 0$$
>
> então $F$ é falsa independentemente de qualquer suposição heurística. Sob $\text{Refines}(F, x)$, o trabalho científico $x$ é refutado com prova construtiva irrefutável.
>
>
>

# 8. Protocolo Experimental e Benchmarks

Para cumprir os requisitos de conferências como o ICLR, o projeto desacopla a avaliação em **dois benchmarks complementares e independentes**, evitando misturar erros de tradução com falhas de raciocínio dedutivo.

```
                      BENCHMARKS DO PROJETO
                                │
        ┌───────────────────────┴───────────────────────┐
        ▼                                               ▼
┌─────────────────────────────────┐   ┌─────────────────────────────────┐
│       PhysFidelityBench         │   │        PhysVerifyBench          │
├─────────────────────────────────┤   ├─────────────────────────────────┤
│ Entrada: Sketch x informal      │   │ Entrada: Termos formais F (DSL) │
│ Objetivo: Avaliar tradução      │   │ Objetivo: Avaliar verificação,  │
│           e fidelidade Refines  │   │           roteamento e oráculos │
│ Validação: Humana Duplo-Cega    │   │ Avaliação: Soundness estrito,   │
│            por Físicos (κ > 0.8)│   │            FPR e Contraexemplos │
└─────────────────────────────────┘   └─────────────────────────────────┘

```

### 8.1. PhysFidelityBench (Avaliação de Tradução Semântica: $x \to F$)

Mede se a rede neural traduz com precisão o que o cientista escreveu sem omitir premissas ou alterar hipóteses físicas.

- **Volume:** 1.200 derivações extraídas do arXiv (`hep-th`, `math-ph`, `gr-qc`, `cond-mat`) e de livros-texto clássicos de física teórica.



- **Processo de Anotação:** Três pesquisadores independentes avaliam se a formalização na DSL preserva a física pretendida ($\text{Refines} \in \\{0, 1\\}$).



- **Métrica:** Concordância inter-anotador via *Cohen’s Kappa* ($\kappa \ge 0.82$) e Acurácia Estrita de Fidelidade.




### 8.2. PhysVerifyBench (Avaliação do Agente e dos Oráculos: $F \to y$)

Mede a capacidade do agente em gerar obrigações de prova, rotear oráculos e emitir vereditos corretos sem alucinações.

- **Volume:** 5.000 instâncias formalizadas diretamente na DSL, estruturadas em 4 eixos principais:



  1. **DimConsistency ($\mathbb{Q}^7$):** Equações de gravidade quântica, teoria quântica de campos e mecânica dos fluidos contendo perturbações dimensionais intencionais sutis.



  2. **HardyAsymptotics:** Regimes limites onde a teoria de perturbação diverge ou muda de comportamento assintótico.



  3. **ProofHoleAudit:** Deduções válidas onde etapas intermediárias foram subtraídas para avaliar a capacidade do sistema em detectar *gaps* não preenchidos.



  4. **CounterExampleSearch:** Hipóteses plausíveis que falham em regiões paramétricas extremas.



- **Hidden Split OOD:** 1.000 instâncias retidas de subáreas nunca vistas no ajuste fino (ex.: biofísica matemática e cosmologia teórica recente pós-2025) para testar generalização fora da distribuição de treino.




### 8.3. Métricas Principais

- **False Accept Rate (FPR):** A métrica mais crítica do paper. É a taxa em que o sistema atesta como válido algo que continha falhas analíticas. O objetivo do NatalIA é derrubar o FPR a níveis próximos de zero ($< 1\\%$).



- **Coverage-Risk Curve (Curva de Risco-Cobertura):** Traça o risco de erro em função da porcentagem de casos em que o modelo emite veredito vs. decide abster-se.



- **Expected Calibration Error (ECE):** Mede o desvio entre a confiança emitida $\hat{p}$ e a taxa real de acerto.



- **Custo Computacional Médio por Instância:** Tempo de CPU/GPU e contagem de passos de inferência.




# 9. Baselines e Ablações Sistemáticas

### Baselines de Comparação

1. **LLMs Puros de Raciocínio (Zero-Shot & Few-Shot):** GPT-4o, Claude 3.5 Sonnet, o1 / Gemini 1.5 Pro com chain-of-thought longo.



2. **Frameworks Auto-Formais Existentes:** Abordagens como Lean Copilot e COPRA (voltadas prioritariamente para matemática pura, sem tipos dimensionais em $\mathbb{Q}^7$ ou foco em física teórica).



3. **LLM + CAS Ingênuo (Sem Orquestração POMDP):** Pipelines padrão que apenas convertem texto para SymPy sem checagem formal ou fragmento de Hardy.




### Matriz de Ablações Essenciais para o Artigo

- **Ablação 1 (Sem a DSL Tipada):** Traduzir rascunhos informais direto para código Python arbitrário, demonstrando o aumento substancial na taxa de falsos aceites decorrente da falta de verificação de tipos.



- **Ablação 2 (Sem Penalidade Assimétrica, $\beta\_{\text{FA}} = 1$):** Treinar a política de RL com pesos uniformes, demonstrando como o sistema passa a chutar vereditos para maximizar cobertura às custas de confiabilidade.



- **Ablação 3 (Sem Abstenção Calibrada):** Forçar o modelo a sempre classificar instâncias de forma binária ($\text{Aceita} \lor \text{Refuta}$), avaliando o colapso nas métricas de segurança epistêmica.



- **Ablação 4 (Sem o Fragmento de Hardy $\mathcal{H}\_E$):** Abrir as regras assintóticas para funções arbitrárias, evidenciando o congelamento do sistema (*timeouts* frequentes) por indecidibilidade analítica.




# 10. Resumo Estruturado do Projeto

| **Dimensão**               | **Especificação do NatalIA**                                                                                                    |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| **Problema Científico**    | Formalização e validação segura de deduções analíticas em física matemática sob incompletude informacional.                     |
| **Formulação Teórica**     | POMDP com espaços de observação simbólicos, ações de síntese/despacho e decisão terminal calibrada.                             |
| **Representação Formal**   | DSL tipada com dimensionalidade em $\mathbb{Q}^7$ e limites assintóticos restritos ao Corpo de Hardy $\mathcal{H}\_E$.          |
| **Motores de Verificação** | Hierarquia de confiança com Lean 4 (ITP), Z3 (SMT), SymPy (CAS) e Aritmética Intervalar rigorosa.                               |
| **Mecanismo de Treino**    | RLVR com recompensa assimétrica ($\beta\_{\text{FA}} \gg 1$), penalização por custo computacional e calibração por Brier score. |
| **Garantias Fornecidas**   | Soundness formal condicional sobre o termo compilado e refutação irrefutável por contraexemplo construtivo.                     |
| **Suíte de Benchmarks**    | *PhysFidelityBench* (fidelidade de tradução $x \to F$) e *PhysVerifyBench* (capacidade de prova, refutação e abstenção).        |
| **Métrica Decisiva**       | Minimização do False Accept Rate (FPR) via curva de risco-cobertura com abstenção calibrada.                                    |

Essa formulação fecha as lacunas conceituais e metodológicas: transforma uma ideia abstrata em um programa de pesquisa de aprendizado neuro-simbólico, munido de rigor matemático, formulação de aprendizado bem delimitada e protocolo experimental reprodutível.
# DSL 1.0 e API

## Submissão

```json
{
  "schema_version": "1.0",
  "title": "Quadrado não negativo",
  "source_latex": "x^2 \\geq 0",
  "variables": {"x": {"dimension": ["0", "0", "0", "0", "0", "0", "0"]}},
  "assumptions": [],
  "claims": [{"kind": "relation", "id": "square", "lhs": "x**2", "op": ">=", "rhs": "0"}],
  "budget_ms": 5000
}
```

`source_latex` é contexto armazenado para comparação humana, sem tradução nem atestado de fidelidade. Todas as variáveis são reais; não há quantidades complexas, tensores, integrais ou quantificadores arbitrários. A relação é universal sob a conjunção das premissas.

Os campos desconhecidos são rejeitados. Máximos: 64 KiB por corpo HTTP, 20 variáveis, 20 premissas, 20 afirmações, 512 caracteres/expressão, 100 nós AST, profundidade 20. Orçamento inteiro de 250–15.000 ms; inclui o início do processo descartável, portanto valores muito baixos podem terminar antes do primeiro solver. Uma consulta Z3 recebe no máximo 2.000 ms e respeita o orçamento remanescente. Campos opcionais: `verification_mode` (`fast` padrão, `certified`) e `critical` (bloqueia aceite Fast sem certificado).

## Expressões e unidades

Operadores: `+`, `-`, `*`, `/`, `**`, sinais unários e parênteses. Números inteiros com módulo ≤ 10⁹; escreva racionais como `1/2`. Floats são rejeitados para evitar exatidão implícita. Nomes de variáveis ASCII declaradas, até 24 caracteres. Sem indexação, atributos, código, importações ou chamadas arbitrárias. O parser usa `ast.parse` seguido de uma lista permitida; nunca executa `eval`, `exec`, `parse_expr` ou `sympify` sobre a entrada.

Dimensões: sete strings racionais na ordem `[M,L,T,I,Θ,N,J]`. Cada expoente possui módulo ≤ 100. Soma exige dimensões iguais; produto soma expoentes; divisão subtrai; potências multiplicam por um racional com módulo ≤ 8. `sqrt` divide a dimensão por dois; `exp`, `log`, `sin`, `cos` exigem argumento adimensional. Unidades naturais/projeções não estão implementadas.

Zero literal é polimórfico **apenas na comparação** (`energia >= 0`). Em somas, use uma expressão dimensionalmente consistente. `0` não permite esconder incompatibilidade dentro de `energia + momento`.

## Afirmações

### `relation`

`lhs`, `op` (`==`, `!=`, `>`, `>=`, `<`, `<=`), `rhs`, `id`, `kind`.

O adaptador Z3 suporta polinômios e expressões racionais com potências inteiras limitadas. Funções transcendentais e potências fracionárias produzem `unknown`, nunca aceite. Antes de avaliar uma relação, o adaptador tenta provar que todos os denominadores são não nulos sob as premissas. Se não consegue, abstém-se. Premissas com divisões potencialmente indefinidas não são suportadas; declare restrições como `x != 0` e coloque a divisão na afirmação.

Para provar: verifica que as premissas são satisfatíveis; depois busca um modelo das premissas e da **negação** da afirmação. `UNSAT` fecha a obrigação relativamente ao Z3/encoding. `SAT` só refuta quando uma atribuição racional pode ser reavaliada independentemente com `Fraction`, verificando também as premissas. Modelos algébricos irracionais ficam abertos até existir um checker apropriado. `unknown`, erro e timeout não certificam.

### `limit`

```json
{"kind":"limit","id":"asymptotic","expression":"(2*x**2+1)/(x**2+3)","variable":"x","target":"infinity","expected":"2"}
```

Adaptador consultivo: expressões racionais e `exp`, uma variável livre, expressão adimensional e limite em +∞. Premissas adicionais, `sin`, `cos`, `log`, raízes e potências fracionárias ficam fora do adaptador. O resultado do SymPy é armazenado, mas **permanece `unknown` mesmo quando coincide com o esperado**. Não se reivindica completude/decidibilidade do corpo de Hardy ou prova de validade eventual de domínio.

### `proof_hole`

```json
{"kind":"proof_hole","id":"lemma","description":"Falta justificar a troca entre limite e integral."}
```

Uma lacuna explicitamente declarada sempre fica aberta. O sistema não descobre automaticamente todas as lacunas de uma dedução informal. IDs são únicos; `compile`, `dimensions`, `premises` e o prefixo `assumption-` são reservados.

## Agregação

| Veredito | Condição |
| --- | --- |
| `INVALID` | Compilação falhou; nenhum solver é despachado |
| `REFUTED` | Pelo menos uma obrigação tem testemunha racional validada sob as premissas |
| `ACCEPTED` | Premissas consistentes e todas as obrigações declaradas certificadas |
| `ABSTAIN` | Qualquer outra situação; incluindo premissas contraditórias e recursos esgotados |

Contraexemplo validado domina lacunas abertas. A aplicação não tenta combinar evidências de Lean/intervalos porque esses adaptadores ainda não existem. `confidence` é sempre `null`, `calibration` é `not_available`; número de obrigações fechadas não é uma probabilidade.

## Endpoints

| Método / rota | Contrato |
| --- | --- |
| `POST /api/runs` | Submissão síncrona (compatível); persiste o job antes do cálculo; HTTP 201 ou 200 se idempotente |
| `POST /api/jobs` | Submissão assíncrona; HTTP 202 com estado operacional |
| `GET /api/jobs/{uuid}` | Progresso; `succeeded` não significa aceite científico |
| `POST /api/jobs/{uuid}/cancel` | Solicita encerramento do processo descartável |
| `GET /api/jobs/{uuid}/events` | SSE de estado operacional; não é certificado |
| `POST /api/certificates/recheck` | Recheck do kernel polinomial, sem Z3 |
| `GET /api/artifacts/{sha256}` | Download isolado por tenant |
| `GET /api/runs?q=&verdict=` | Histórico com busca e filtro |
| `GET /api/runs?limit=20&offset=0` | Resumos paginados; limite 1–100 |
| `GET /api/runs/{uuid}` | Entrada, resultado, evidências, SMT-LIB e spans |
| `GET /api/examples` | Nove exemplos e vereditos esperados |
| `GET /api/stats` | Estatísticas persistidas; workers ativos deste processo |
| `GET /api/capabilities` | Disponibilidade e limites explícitos |
| `GET /health/live` | Processo responde |
| `GET /health/ready` | Schema SQLite acessível |
| `GET /metrics` | Exposição Prometheus |
| `GET /docs`, `/openapi.json` | Contrato gerado pelo FastAPI |

Erros: 413 (corpo), 422 (schema), 429 (capacidade), 403 (origem), 404 (execução ausente), 409 (idempotência), 500 (falha interna/persistência), 503 (readiness). Um erro de compilação de DSL válido no esquema retorna 201 com `INVALID` e fica no histórico. Cabeçalho `Idempotency-Key` reutiliza a execução se o conteúdo coincidir; conteúdo diferente com a mesma chave devolve 409. `job_status=succeeded` significa que o cálculo terminou, não que a afirmação foi aceita.

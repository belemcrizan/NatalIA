# Contrato de confiança natalia-trust-1.0

Estado operacional, conclusão científica e garantia da evidência são campos distintos.

| Eixo | Valores | Significado |
| --- | --- | --- |
| Job | `queued`, `running`, `succeeded`, `failed`, `cancelled`, `timed_out`, `rejected` | A execução terminou ou não. `succeeded` não aceita a afirmação. |
| Conclusão | `ACCEPTED`, `REFUTED`, `INVALID`, `ABSTAIN` | Veredito sobre a obrigação formalizada. |
| Garantia | `SMT_RELATIVE`, `EXACT_WITNESS_CHECKED`, `INTERVAL_ENCLOSURE`, `KERNEL_CHECKED`, `STATIC_COMPILE`, `ADVISORY`, `UNAVAILABLE` | O que a evidência realmente autoriza. |

## Fast vs Certified

**Fast** pode aceitar no fragmento SMT. A garantia permanece `SMT_RELATIVE`. Refutações com testemunha racional independente são `EXACT_WITNESS_CHECKED`.

**Certified** recusa aceite baseado só em UNSAT do solver. Aceite exige `KERNEL_CHECKED` no fragmento polinomial (identidade ou soma/quadrado em ℚ), ligado ao hash da obrigação original. Não há downgrade silencioso para Fast: se o certificado falta, a conclusão é `ABSTAIN` e o job pode mesmo assim ser `succeeded`.

Obrigações `critical=true` não aceitam sem `KERNEL_CHECKED`, mesmo em Fast.

## Independência

Um kernel comprova a proposição formal. Isso não demonstra que ela expressa o artigo, a intenção do usuário ou a física.

Hash é integridade do conteúdo persistido. Recheck é reexecução do checker. Assinatura (quando existir) é proveniência. Nenhum desses itens é verdade matemática por si.

## TCB do caminho certificado local

- Parser e elaborador (`natalia.dsl`)
- Compilador dimensional (`natalia.compile` / `engine` compile)
- Kernel polinomial (`natalia.kernel`)
- Runtime Python e aritmética `Fraction`
- Sistema operacional e o processo worker

Não está neste TCB: Z3 (não fecha aceite Certified), SymPy, Lean (exportação opcional, `sorry` rejeitado), modelos de linguagem.

Lean 4, se instalado, pode checar um arquivo exportado. Sem toolchain e sem Mathlib, o NatalIA **não** reporta `KERNEL_CHECKED` via Lean.

## SMT

Z3 5.x neste repositório não é tratado como produtor universal de Alethe/LFSC. Enquanto não houver caminho produtor–formato–checker exercitado para o fragmento QF_NRA usado aqui, o aceite SMT permanece relativo ao solver.

## Cache

A chave inclui payload normalizado, modo, contrato de confiança, política e versões. Fast nunca é reutilizado como Certified. Cache compartilhado entre tenants não está habilitado.

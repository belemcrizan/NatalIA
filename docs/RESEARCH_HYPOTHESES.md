# Hipóteses da vertical 0.4 (álgebra com dimensões)

Não são teoremas publicados. Critérios de refutação são operacionais.

1. **Kernel independente detecta integração errada.** Baseline: aceite Fast SMT. Intervenção: recheck do certificado com obrigação diferente ou adulterada. Dados: `tests/test_trust.py`. Métrica: rejeição. Refutação: recheck aceita hash ou testemunha adulterados.

2. **Tipagem dimensional evita solver em mistura M/L.** Já coberto por regressão `INVALID` sem span Z3. Refutação: despacho Z3 após erro dimensional.

3. **Certified não promove SMT.** Energia cinética com `m>0` é Fast ACCEPTED e Certified ABSTAIN. Refutação: Certified ACCEPTED com `guarantee_level=SMT_RELATIVE`.

Ameaça à validade: fragmento kernel pequeno; corpus sintético; sem revisão humana independente nesta fatia.

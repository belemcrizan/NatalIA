# Lean 4 bounded certification fragment

Pinned toolchain: `lean-toolchain` (`leanprover/lean4:v4.15.0`).
No Mathlib. No PhysLean. No user-uploaded Lean.

## What is proved

| Layer | Statement | Status |
| --- | --- | --- |
| Algebraic positivity | `∀ x : Int, 0 ≤ x * x` | In `NatalIA/Polynomial.lean` |
| Dissipative term sign | `c ≥ 0 → 0 ≤ c * v * v` over `Int` | In `NatalIA/Dissipation.lean` |
| Energy derivative / non-increase | `dE/dt ≤ 0` along the damped oscillator | **Not proved.** The DSL has no derivative operator. |

A checked integer lemma is not a certificate for a real-valued, dimensioned NatalIA claim unless the backend mapping accepts that exact fragment.

## Independent recheck

```bash
cd formal
lake build
```

The API Lean path requires the same lakefile, approved imports, theorem names `NatalIA.int_sq_nonneg` or `NatalIA.dissipative_term_nonneg`, a sorry-free kernel check, and an axiom audit against the declared policy. Process exit code alone is not acceptance.

Experimental `sorry` exports in `natalia.lean` remain a separate artifact type and never become `KERNEL_CHECKED`.

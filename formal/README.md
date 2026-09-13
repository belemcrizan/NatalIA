# NatalIA kernel fragment (optional Lean export)

The certified path in NatalIA 0.4 is `natalia.kernel`, an independent polynomial
identity / sum-of-squares checker over Q. Lean files, when generated, are
**exports bound to an obligation hash**. They are not certificates until a Lean
4 toolchain with approved imports checks a sorry-free file.

This directory is a placeholder for a future lakefile pin. It is intentionally
empty of proofs so a missing Lean install cannot be mistaken for a green kernel.

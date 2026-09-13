# NatalIA kernel fragment (optional Lean export)

The certified path in NatalIA is `natalia.kernel`, an independent polynomial
identity / sum-of-squares checker over Q. Lean files are exports bound to an
obligation hash. They contain an explicit `sorry` so an installed `lean` binary
cannot accept a comment-only file as a kernel certificate.

Check command actually used: `lean Obligation.lean`. The checklist phrase
`lean --check` is treated as mandatory-checking intent.

This directory still has no lakefile pin and no Mathlib. Absence of proofs here
is intentional.

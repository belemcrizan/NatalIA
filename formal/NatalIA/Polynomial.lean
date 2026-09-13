/-
  NatalIA integer positivity fragment (lean4_int_poly_pos_v1).

  Domain: integers, not the DSL's default real encoding.
  This file is the only approved statement/proof surface for the Lean path.
  Users cannot upload Lean; the backend copies this library into a restricted check.
-/
namespace NatalIA

/-- Squares are nonnegative over ℤ. This is not a theorem about ℝ. -/
theorem int_sq_nonneg (x : Int) : 0 ≤ x * x :=
  Int.mul_self_nonneg x

end NatalIA

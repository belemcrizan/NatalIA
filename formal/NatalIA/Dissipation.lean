/-
  Layer 1 of the damped-oscillator vertical: sign of the dissipative term.

  Proved: if c ≥ 0 over ℤ, then c * v * v ≥ 0.
  Not proved: ODE, chain rule, dE/dt, or mechanical-energy non-increase on an interval.
-/
namespace NatalIA

theorem dissipative_term_nonneg (c v : Int) (hc : 0 ≤ c) : 0 ≤ c * (v * v) := by
  have hv : 0 ≤ v * v := Int.mul_self_nonneg v
  exact Int.mul_nonneg hc hv

end NatalIA

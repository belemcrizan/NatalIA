export function TrustPage() {
  return (
    <div className="mx-auto max-w-3xl space-y-4">
      <h1 className="text-2xl font-semibold">Trust contract</h1>
      <p>Job status, scientific conclusion, and evidence guarantee are distinct (natalia-trust-1.0).</p>
      <section>
        <h2 className="text-lg font-semibold">Available in this delivery</h2>
        <ul className="list-disc pl-5">
          <li>JSON DSL with a restricted AST; no JavaScript eval of user expressions.</li>
          <li>Exact dimensional algebra in ℚ⁷.</li>
          <li>Z3 over real arithmetic with consistent assumptions.</li>
          <li>Independently re-evaluated rational counterexamples.</li>
          <li>SymPy limits as advisory evidence.</li>
          <li>Fast vs Certified; SMT is not reused as Certified.</li>
        </ul>
      </section>
      <section>
        <h2 className="text-lg font-semibold">Not claimed</h2>
        <ul className="list-disc pl-5">
          <li>Lean 4 with Mathlib without sorry.</li>
          <li>Natural-language or PDF autoformalization.</li>
          <li>Full ODE proofs from polynomial inequalities.</li>
          <li>Probabilistic calibration.</li>
        </ul>
      </section>
    </div>
  );
}

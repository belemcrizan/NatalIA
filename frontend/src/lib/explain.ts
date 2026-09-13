import type { GuaranteeLevel, Obligation, RunDocument, Verdict } from "./types";

const TITLES: Record<Verdict, string> = {
  ACCEPTED: "The solver accepted this formal statement under the listed assumptions.",
  REFUTED: "The claim fails for this exact value.",
  INVALID: "These terms have incompatible units or the expression is not in the supported fragment.",
  ABSTAIN: "The selected verification method could not establish this claim.",
};

const LIMITS: Record<Verdict, string> = {
  ACCEPTED:
    "Acceptance is relative to the declared encoding. It is not an experimental measurement and SMT-relative success is not KERNEL_CHECKED.",
  REFUTED: "A checked counterexample rejects a universal claim. A plotted curve is not the certificate.",
  INVALID: "Compile-time rejection is not a mathematical refutation of a well-typed statement.",
  ABSTAIN: "Inconclusive is not a hidden proof. Do not treat an open hole or contradictory premises as acceptance.",
};

export function conclusionTitle(run: RunDocument) {
  if (run.job_status && run.job_status !== "succeeded") {
    return `Operational state: ${run.job_status}. This is not a scientific conclusion.`;
  }
  return TITLES[run.verdict] ?? "The run finished without a mapped conclusion.";
}

export function conclusionLimit(verdict: Verdict) {
  return LIMITS[verdict];
}

export function guaranteeNote(level?: GuaranteeLevel | null) {
  switch (level) {
    case "SMT_RELATIVE":
      return "Relative to the Z3 encoding and stated premises. Not an independent kernel certificate.";
    case "EXACT_WITNESS_CHECKED":
      return "A rational assignment was re-evaluated with exact arithmetic, independently of the solver status.";
    case "INTERVAL_ENCLOSURE":
      return "Exact rational box enclosure on a declared finite domain. Not a global real-line certificate.";
    case "KERNEL_CHECKED":
      return "An independent checker accepted a proof object bound to this obligation hash.";
    case "STATIC_COMPILE":
      return "Dimensional or AST rejection before solvers.";
    case "ADVISORY":
      return "Informative only. Must not be promoted to a certificate.";
    case "UNAVAILABLE":
      return "The requested checker was not run or is not installed.";
    default:
      return "Guarantee not reported on this record.";
  }
}

export function obligationSummary(item: Obligation) {
  if (item.counterexample) {
    const values = Object.entries(item.counterexample)
      .map(([key, value]) => `${key} = ${value}`)
      .join(", ");
    return `The claim fails for this exact value: ${values}.`;
  }
  if (item.status === "invalid" && /dimension/i.test(item.reason ?? "")) {
    return "These terms have incompatible units.";
  }
  if (item.status === "declared_gap") {
    return "A declared proof hole blocked acceptance.";
  }
  return item.reason || `${item.id}: ${item.status}`;
}

export function nextActions(verdict: Verdict) {
  switch (verdict) {
    case "REFUTED":
      return "Inspect the exact rational witness, then revise the domain or the claim.";
    case "INVALID":
      return "Fix units or the expression, then compile again before running solvers.";
    case "ABSTAIN":
      return "Add missing assumptions, close proof holes, or stay in Fast mode without claiming a certificate.";
    default:
      return "Read the guarantee, then export or recheck a kernel certificate if one exists.";
  }
}

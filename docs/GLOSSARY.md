# NatalIA Terminology Glossary

This glossary establishes the canonical English terminology used across NatalIA interfaces, APIs, documentation, diagnostics, and test suites.

---

## Core Product Terms

### Claim
A specific mathematical or physical statement asserted about a system (e.g., an inequality, equality, or limit). A submission may contain one or more claims to be evaluated.

### Assumptions
The mathematical and physical premises under which a claim is evaluated (e.g., mass $m > 0$, velocity $v \in \mathbb{R}$). Contradictory assumptions must never silently produce a misleading acceptance.

### Formalization
The explicit, machine-checkable representation of variables, dimensions, assumptions, and claims expressed in NatalIA's restricted AST/JSON DSL. The formalization is the sole object evaluated by solvers; proof of formalization does not prove that informal text or physics was accurately modeled.

### Verification
The process of discharging formal obligations through automated reasoning engines, satisfiability modulo theories (SMT) solvers, polynomial identity kernels, or certified checkers within a bounded resource budget.

### Conclusion
The scientific determination reached regarding a formal claim under stated assumptions:
- **ACCEPTED**: All declared obligations are satisfied within the supported fragment.
- **REFUTED**: A valid counterexample violates at least one claim while satisfying all assumptions.
- **INVALID**: The formalization contains syntactic, dimensional, or typing errors; no solvers are dispatched.
- **INCONCLUSIVE** (machine-readable `ABSTAIN`): The available evidence cannot close the investigation (e.g., timeout, unsupported operator, unproven domain safety, or solver budget exhaustion). A timeout is never a refutation.

### Evidence
The inspectable, verifiable artifacts supporting a conclusion, such as exact rational counterexample coordinates, kernel certificates, SMT-LIB scripts, or dimension matrices.

### Guarantee
The precise epistemic assurance level provided by the verification mechanism:
- **SMT_RELATIVE**: Acceptance holds relative to the external SMT solver (Z3) without an independent certificate.
- **EXACT_WITNESS**: A rational counterexample was independently verified via exact rational arithmetic.
- **KERNEL_CHECKED**: An independent verified polynomial / sum-of-squares certificate was validated by NatalIA's internal kernel.
- **ADVISORY**: Indicative calculation (e.g., SymPy limits) without formal certification.

### Counterexample
A concrete numerical assignment to variables that satisfies all declared assumptions but falsifies a claim. Counterexamples in NatalIA are evaluated using exact rational fractions ($\mathbb{Q}$) to prevent floating-point rounding illusions.

### Inconclusive
The human-facing explanation for `ABSTAIN`. An inconclusive result indicates that formal obligations remain open or operational bounds were exceeded; it never implies refutation or falsity.

### Job
An asynchronous unit of execution tracking operational state (`queued`, `running`, `succeeded`, `failed`, `cancelled`, `timed_out`, `rejected`), persistence, leases, and real-time progress events. Operational job completion is strictly separated from scientific claim acceptance.

### Verification History
The durable, tamper-evident log of past verification runs, submissions, verdicts, and evidence records stored in relational storage (SQLite locally, Cloud SQL in cloud deployments).

---

## Operational & Architectural Terms

| Term | Definition |
| --- | --- |
| **Local Profile** | Default execution mode on loopback (`127.0.0.1`) with in-process workers and SQLite storage. Requires no cloud credentials, API keys, or GPU. |
| **Distributed Profile** | Multi-tenant execution mode with authenticated API keys, tenant isolation, and durable worker dispatching. |
| **Trusted Computing Base (TCB)** | The minimal set of components that must be correct for a verification result to be trusted. |
| **Outbox** | Transactional event storage ensuring reliable, at-least-once delivery of job status events. |

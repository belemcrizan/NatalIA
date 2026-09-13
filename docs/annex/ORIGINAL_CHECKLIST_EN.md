# Complete 10/10 Vision Checklist — NatalIA (English Companion Translation)

*Note: This document is an authoritative English companion to the historical document preserved in `docs/annex/ORIGINAL_CHECKLIST.md`. The original Portuguese document is retained verbatim for forensic provenance and SHA-256 traceability integrity.*

---

## Overview

Below is the complete roadmap detailing future domains and engineering tasks, categorized by priority and domain:
- **P0**: Core blocker / Essential foundation
- **P1**: Critical for production scale
- **P2**: Important capability
- **P3**: Desirable extension

---

## 0. Conceptual Foundations
- **P0** Define the core scientific thesis in a single sentence: *"Automated and certified formal verification of scientific knowledge at scale."*
- **P0** Establish field nomenclature: *Verified Science* or *Formal Scientific Computing*.
- **P0** Author a 4–8 page position paper defining the field, open problems, and 10-year research agenda.
- **P0** Explicit negative scope: what NatalIA *does not* do (raw unconstrained LaTeX, automated fidelity proofs between paper and formal model, empirical physical validity).
- **P1** Define 3 initial verticals: pure mathematics, theoretical physics, engineering and control theory.
- **P1** Define 3 future verticals: quantitative finance, computational chemistry, systems biology.
- **P2** Determine governance model: pure open source, open core, or non-profit foundation.
- **P2** Define licensing framework (Apache 2.0, MIT, AGPL, or dual license).
- **P2** Define patent and IP policy (defensive patent pledge or foundation assignment).

---

## 1. Certification & Epistemic Trust
### 1.1 Independent Kernel
- **P0** Interface with standard external proof kernels: Lean 4, Coq, Isabelle, HOL Light, or Metamath.
- **P0** If maintaining an internal polynomial kernel, formalize its mathematical soundness with published machine proofs.
- **P0** Keep the kernel *small, simple, and auditable*: < 5,000 lines of code.
- **P0** Publish kernel soundness proofs in peer-reviewed formal methods venues (ITP, CPP, CAV, LICS).
- **P1** Minimize the Trusted Computing Base (TCB) to: kernel + checker + parser + hardware. Document every line.
- **P1** Formalize DSL parser semantics in Lean/Coq with semantics preservation theorems.
- **P1** Formalize AST-to-SMT compiler with correctness proofs.

### 1.2 SMT Certification
- **P0** Implement Z3 to Alethe proof reconstruction.
- **P0** Integrate an independent Alethe proof checker (e.g. Carcara).
- **P0** Provide Z3 to LFSC / Dedukti translation pathways.
- **P1** Continuous integration gate rejecting unverified SMT proofs.
- **P1** Support multi-solver verification with cvc5, Vampire, and E.
- **P2** Implement portfolio solver orchestration with fragment-specific selection.

### 1.3 Interactive Theorem Prover (Lean 4) Integration
- **P0** Mandatory `lean --check` validation in CI for exported proof skeletons.
- **P0** Mathlib and PhysLean pinned to specific immutable commit hashes in `lakefile`.
- **P0** Differential testing between AST semantics and Lean formulations.
- **P1** Exporters for Coq, Isabelle/HOL, and HOL Light.

### 1.4 Cryptographic Attestation
- **P0** Digitally sign verification evidence artifacts with Sigstore/Cosign.
- **P0** Generate SLSA Level 3 supply-chain attestations.
- **P0** Publish public transparency logs (Rekor).
- **P1** Implement Merkle trees of verification results for verifiable batch auditing.

---

## 2. Scientific Core & Mathematical Expressiveness
### 2.1 Physics & Dimensional Formalization
- **P0** Exact dimensional algebra over rational vector spaces $\mathbb{Q}^7$.
- **P0** Support full SI prefixes, compound derived units, and natural unit systems ($c = \hbar = G = 1$).
- **P0** Dimensional validation for differential operators, tensor contractions, and integrals.
- **P1** Automatic dimensional conservation checking across physical dynamical systems.

### 2.2 Mathematical Fragments
- **P0** Real algebraic geometry: QF_NRA with cylindrical algebraic decomposition (CAD).
- **P0** Real non-linear interval arithmetic with guaranteed enclosure (dReal / delta-sat).
- **P0** Exact rational arithmetic for all witness points and counterexamples.
- **P1** Ordinary differential equations (ODEs) with verified reachability and enclosures.
- **P1** Asymptotic analysis with formal Big-O/Omega/Theta certificates.

---

## 3. Auto-Formalization & Human-in-the-Loop Review
- **P0** Neural translation must be strictly separated from verification; LLM output is untrusted input.
- **P0** Formalization review gate: Every automated translation requires human sign-off before solver dispatch.
- **P1** Iterative repair loops: Syntax, typing, or dimensional errors fed back to model for correction.
- **P1** Grounded source citation: Map formal obligations back to specific lines and equations in source documents.

---

## 4. Benchmarking & Empirical Evaluation
- **P0** Expand benchmark corpus (PhysVerifyBench) to diverse physical and mathematical domains.
- **P0** Separate evaluation sets with strict holdout custody to prevent data contamination.
- **P1** Measure False Positive Rate (FPR) and Expected Calibration Error (ECE).
- **P1** Continuous regression tracking on solver performance, solving times, and memory consumption.

---

## 5. Cloud Architecture & Infrastructure (GCP Path)
- **P0** Containerized microservices running on Google Cloud Run with scale-to-zero capabilities.
- **P0** Managed relational database: Cloud SQL for PostgreSQL replacing local SQLite.
- **P0** Immutable object storage: Google Cloud Storage (GCS) for certificate and artifact archives.
- **P0** Centralized secrets management via Google Secret Manager.
- **P1** Asynchronous task distribution via Google Cloud Tasks / Pub/Sub.
- **P1** Distributed telemetry with OpenTelemetry (OTel), Cloud Trace, and structured audit logs.

---

## 6. Security, Isolation & Multi-Tenancy
- **P0** Strict multi-tenant data segregation enforced at the database and object storage layers.
- **P0** Unprivileged container execution (`natalia:natalia`, UID 10001) with read-only root filesystems.
- **P0** Strict Content Security Policy (CSP) blocking external unauthorized scripts.
- **P1** Solver subprocess sandboxing with memory, CPU, and wall-clock execution limits.
- **P1** OpenID Connect (OIDC) authentication and role-based access control (RBAC).

---

## Summary & Delivery Philosophy

1. **Evidence Precedes Verdict**: A conclusion without an inspectable, re-evaluatable certificate is incomplete.
2. **Epistemic Modesty**: Clearly distinguish solver-relative satisfaction (`SMT_RELATIVE`), independent kernel certification (`KERNEL_CHECKED`), verified counterexamples (`EXACT_WITNESS_CHECKED`), and heuristic computations (`ADVISORY`).
3. **Local-First, Cloud-Ready**: Deliver a first-class local research experience on Windows, macOS, and Linux, with a clear, validated deployment path to Google Cloud Platform.

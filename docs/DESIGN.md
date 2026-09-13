# Design rationale — scientific exploration UI

NatalIA’s previous home screen was a three-column operations dashboard: featured
cases, recent runs, and local environment. That layout treated verification as
administration. The redesign starts from a single scientific question and
discloses evidence progressively.

## Information architecture

1. **Home** states what the laboratory does, the three user-facing conclusions,
   and a compact Fast vs Certified note. System health is a utility page.
2. **Guided examples** are filterable investigation cards with domain,
   difficulty, expected outcome, time, and an equation cue. They are labeled
   educational models, never “real-world validated”.
3. **Investigation pages** follow the narrative: question, model, equations,
   optional illustrative chart, the exact obligation in English, run, result,
   advanced JSON.
4. **Claim builder** remains the structured DSL form. Advanced JSON is visually
   secondary. There is no fake natural-language box.

## Honesty constraints

Charts are marked illustrative. Rendered MathML is generated from curated
templates, not from arbitrary user HTML. Tier 4 (damped dissipation) is an
explicit proof hole (`ABSTAIN`), not an algebraic stand-in labeled `ACCEPTED`.
The RC page verifies dimensional legality of `t/(R C)`, not the charging ODE.

## Visual system

Neutral paper surfaces, ink text, one green-black accent, semantic badges with
text labels. Compact top navigation, a readable content column, SVG charts with
data tables. No CDN, no new frontend framework.

## Screenshots from the running application

Captured by `python scripts/e2e.py` against a local API (desktop 1440px, mobile 390px):

- `docs/ui/home-desktop.png` / `docs/ui/home-mobile.png`
- `docs/ui/library-desktop.png`
- `docs/ui/investigation-desktop.png`
- `docs/ui/laboratory-desktop.png` / `docs/ui/laboratory-mobile.png`
- `docs/ui/counterexample-desktop.png`
- `docs/ui/observability-desktop.png` (System health)


- Time derivatives and Lyapunov decrease along ODE flows
- SMT support for `exp` as a verified charging law
- Lean/Mathlib certificates without `sorry`
- Natural-language or PDF autoformalization
- Interactive physics simulation
- Probabilistic calibration

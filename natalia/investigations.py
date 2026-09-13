"""Curated scientific investigations for the guided UI.

Educational models only. Provenance is synthetic and versioned with this
repository. These cases do not claim experimental validation.
"""

from __future__ import annotations

SCHEMA = "natalia-investigations-1.1"
CONTENT_VERSION = "1.1.0"

ZERO = ["0"] * 7
M = ["1", "0", "0", "0", "0", "0", "0"]
L = ["0", "1", "0", "0", "0", "0", "0"]
T = ["0", "0", "1", "0", "0", "0", "0"]
V = ["0", "1", "-1", "0", "0", "0", "0"]
E = ["1", "2", "-2", "0", "0", "0", "0"]
P = ["1", "1", "-1", "0", "0", "0", "0"]
K = ["1", "0", "-2", "0", "0", "0", "0"]  # N/m = kg s^-2
VOLT = ["1", "2", "-3", "-1", "0", "0", "0"]
OHM = ["1", "2", "-3", "-2", "0", "0", "0"]
FARAD = ["-1", "-2", "4", "2", "0", "0", "0"]
DAMPING = ["1", "0", "-1", "0", "0", "0", "0"]  # N s / m = kg/s
AMP = ["0", "0", "0", "1", "0", "0", "0"]

SOURCE = {
    "kind": "synthetic_educational",
    "author": "NatalIA maintainers",
    "license": "Same as this repository",
    "note": (
        "Original didactic formalizations. Not copied from copyrighted problem sets "
        "and not labeled as experimentally validated."
    ),
}


def _rel(claim_id, lhs, op, rhs):
    return {"kind": "relation", "id": claim_id, "lhs": lhs, "op": op, "rhs": rhs}


def _sub(title, latex, variables, assumptions, claims, budget=5000, mode="fast"):
    return {
        "schema_version": "1.0",
        "title": title,
        "source_latex": latex,
        "variables": variables,
        "assumptions": assumptions,
        "claims": claims,
        "budget_ms": budget,
        "verification_mode": mode,
    }


def _eq(latex, plain, mathml, caption):
    return {"latex": latex, "plain": plain, "mathml": mathml, "caption": caption}


def _inv(**kwargs):
    kwargs.setdefault("schema", SCHEMA)
    kwargs.setdefault("content_version", CONTENT_VERSION)
    kwargs.setdefault("source", SOURCE)
    kwargs.setdefault("educational_model", True)
    kwargs.setdefault("real_world_validated", False)
    kwargs.setdefault("verification_mode", "fast")
    kwargs.setdefault("charts", [])
    kwargs.setdefault("related", [])
    kwargs.setdefault("planned", [])
    kwargs.setdefault("educational_objective", "formalize-and-check")
    kwargs.setdefault("visualization", "diagram" if not kwargs.get("charts") else "plot")
    kwargs.setdefault("prerequisites", ["NatalIA DSL basics", "distinction between job status and scientific verdict"])
    kwargs.setdefault(
        "application_context",
        kwargs.get("why_it_matters") or "Educational laboratory exercise.",
    )
    kwargs.setdefault(
        "measured_vs_model",
        "No measured dataset is used. The payload is an idealized model written for this repository.",
    )
    kwargs.setdefault("common_mistakes", ["Reading SMT acceptance as an independent proof certificate"])
    kwargs.setdefault("variation", "Change one assumption and compare the new verdict.")
    kwargs.setdefault("source_ids", ["src-natalia-maintainers"])
    kwargs.setdefault("validation_method", "Exact payload verified with natalia.engine.verify against expected_verdict")
    kwargs.setdefault("content_review", "maintainer-reviewed-v1.1")
    kwargs.setdefault("capability", "runnable")
    return kwargs


INVESTIGATIONS = [
    _inv(
        id="inv-01-kinetic",
        example_id="01-energy",
        title="Can kinetic energy be negative?",
        domain="Classical Mechanics",
        difficulty="Foundations",
        tier=1,
        learning_minutes=4,
        question="Can classical kinetic energy be negative when mass is positive?",
        why_it_matters=(
            "Kinetic energy is written as a square scaled by a positive mass. "
            "If the formula is taken as the model, negativity would require a negative square."
        ),
        model=(
            "Point-mass Newtonian kinematics. Mass is a positive scalar. Velocity is a signed "
            "one-dimensional speed. Relativity, rotation, and constraints are out of scope."
        ),
        obligation_english=(
            "Under m > 0, the declared expression m v² / 2 is greater than or equal to zero "
            "for every real velocity v."
        ),
        expected_verdict="ACCEPTED",
        expected_label="Accepted",
        guarantee_level="SMT_RELATIVE",
        limitations=(
            "Acceptance is relative to the SMT encoding of this polynomial inequality. "
            "It does not define energy outside the written formula and does not prove relativistic kinematics."
        ),
        variables_explained=[
            {"name": "m", "meaning": "mass", "unit": "kg"},
            {"name": "v", "meaning": "velocity", "unit": "m/s"},
        ],
        equations=[
            _eq(
                r"E_k = \frac{1}{2} m v^2",
                "E_k = (1/2) m v^2",
                "<math display='block'><msub><mi>E</mi><mi>k</mi></msub><mo>=</mo>"
                "<mfrac><mn>1</mn><mn>2</mn></mfrac><mi>m</mi><msup><mi>v</mi><mn>2</mn></msup></math>",
                "Declared kinetic energy for a point mass.",
            )
        ],
        charts=[
            {
                "id": "ke-vs-v",
                "kind": "quadratic",
                "role": "illustrative",
                "title": "Kinetic energy versus velocity",
                "subtitle": "Illustrative curve for a fixed positive mass m = 2 kg. Not a verified plot.",
                "x_label": "v (m/s)",
                "y_label": "E_k (J)",
                "samples": [
                    {"v": str(x), "Ek": str((2 * x * x) / 2)} for x in range(-4, 5)
                ],
            }
        ],
        submission=_sub(
            "Non-negative kinetic energy",
            r"E_k = \frac{1}{2} m v^2 \geq 0,\quad m>0",
            {"m": {"dimension": M}, "v": {"dimension": V}},
            [{"lhs": "m", "op": ">", "rhs": "0"}],
            [_rel("kinetic-energy", "m*v**2/2", ">=", "0")],
        ),
        related=["inv-04-spring", "inv-03-dimensions"],
        source_ids=["src-openstax-up1-7-2", "src-bipm-si-brochure", "src-natalia-maintainers"],
        capability="runnable",
        expected_by_mode={
            "fast": "ACCEPTED",
            "certified": "depends on kernel fragment; not assumed",
            "lean": "ABSTAIN (reals with dimensions are outside lean4_int_poly_pos_v1)",
        },
    ),
    _inv(
        id="inv-02-counterexample",
        example_id="02-counterexample",
        title="When does a squared number become smaller?",
        domain="Mathematics",
        difficulty="Foundations",
        tier=1,
        learning_minutes=5,
        question="Is x² ≥ x true for every real number?",
        why_it_matters=(
            "A universal claim fails as soon as one point in the domain violates it. "
            "NatalIA reports a checked rational witness rather than a vague rejection."
        ),
        model="Unrestricted real arithmetic. No positivity or integer hypothesis is declared.",
        obligation_english="The inequality x² ≥ x holds for every real x.",
        expected_verdict="REFUTED",
        expected_label="Refuted",
        guarantee_level="EXACT_WITNESS_CHECKED",
        limitations=(
            "The witness is a single rational point. A plotted parabola is an illustration, not the certificate."
        ),
        variables_explained=[{"name": "x", "meaning": "real variable", "unit": "dimensionless"}],
        equations=[
            _eq(
                r"x^2 \geq x \quad \forall x \in \mathbb{R}",
                "x^2 >= x for all real x",
                "<math display='block'><msup><mi>x</mi><mn>2</mn></msup><mo>≥</mo><mi>x</mi>"
                "<mo>,</mo><mtext> for every real x</mtext></math>",
                "Claimed for the whole real line, with no extra assumption.",
            )
        ],
        charts=[
            {
                "id": "square-minus-linear",
                "kind": "quadratic",
                "role": "illustrative",
                "title": "Why x² − x dips below zero",
                "subtitle": "Illustrative values of x² − x. The independent checker uses an exact rational point, not this drawing.",
                "x_label": "x",
                "y_label": "x² − x",
                "highlight": "1/2",
                "samples": [
                    {"x": str(x / 2), "y": str((x / 2) ** 2 - (x / 2))} for x in range(-2, 7)
                ],
            }
        ],
        submission=_sub(
            "x**2 >= x for reals",
            r"x^2 \geq x \quad \forall x \in \mathbb{R}",
            {"x": {"dimension": ZERO}},
            [],
            [_rel("square-ge-id", "x**2", ">=", "x")],
        ),
        related=["inv-09-domain"],
        capability="negative_boundary",
        source_ids=["src-natalia-maintainers"],
        expected_by_mode={"fast": "REFUTED", "certified": "REFUTED if independent witness", "lean": "ABSTAIN"},
    ),
    _inv(
        id="inv-03-dimensions",
        example_id="03-dimensions",
        title="Why can't energy and momentum be added?",
        domain="Dimensional Analysis",
        difficulty="Foundations",
        tier=1,
        learning_minutes=4,
        question="Can energy and momentum be added?",
        why_it_matters=(
            "Physical sums require matching dimensions. NatalIA refuses the expression before a solver runs."
        ),
        model="SI base-dimension vectors in Q⁷. No unit-scale conversion is performed.",
        obligation_english=(
            "The mixed expression (1/2) m v² + m v is a well-formed quantity comparable to zero."
        ),
        expected_verdict="INVALID",
        expected_label="Invalid",
        guarantee_level="STATIC_COMPILE",
        limitations="A dimension preset is not a conversion between joules and newton-seconds.",
        variables_explained=[
            {"name": "m", "meaning": "mass", "unit": "kg"},
            {"name": "v", "meaning": "velocity", "unit": "m/s"},
        ],
        equations=[
            _eq(
                r"\tfrac12 m v^2 + m v \geq 0",
                "(1/2) m v^2 + m v >= 0",
                "<math display='block'><mfrac><mn>1</mn><mn>2</mn></mfrac><mi>m</mi>"
                "<msup><mi>v</mi><mn>2</mn></msup><mo>+</mo><mi>m</mi><mi>v</mi><mo>≥</mo><mn>0</mn></math>",
                "Energy plus momentum is not a legal sum.",
            )
        ],
        charts=[
            {
                "id": "units-mismatch",
                "kind": "units",
                "role": "illustrative",
                "title": "Why the sum is rejected",
                "subtitle": "Illustrative comparison of SI dimension vectors. Compile-time rejection is the evidence.",
                "rows": [
                    {"quantity": "(1/2) m v²", "unit": "J", "vector": "M L² T⁻²"},
                    {"quantity": "m v", "unit": "kg·m/s", "vector": "M L T⁻¹"},
                ],
            }
        ],
        submission=_sub(
            "Energy added to momentum",
            r"\tfrac12 m v^2 + m v \geq 0",
            {"m": {"dimension": M}, "v": {"dimension": V}},
            [{"lhs": "m", "op": ">", "rhs": "0"}],
            [_rel("mixed", "m*v**2/2 + m*v", ">=", "0")],
        ),
        related=["inv-01-kinetic", "inv-06-rc"],
        capability="negative_boundary",
        source_ids=["src-bipm-si-brochure", "src-natalia-maintainers"],
        expected_by_mode={"fast": "INVALID", "certified": "INVALID", "lean": "INVALID or ABSTAIN"},
    ),
    _inv(
        id="inv-04-spring",
        example_id=None,
        title="What changes when a spring gets stiffer?",
        domain="Classical Mechanics",
        difficulty="Intermediate",
        tier=2,
        learning_minutes=5,
        question="Under stated assumptions, is U = ½ k x² non-negative?",
        why_it_matters=(
            "Hooke's-law potential is another scaled square. The check is algebraic, not a derivation of Hooke's law."
        ),
        model=(
            "Linear spring with stiffness k > 0 and displacement x. The potential is defined as ½ k x². "
            "Plasticity, gravity, and three-dimensional constraints are out of scope."
        ),
        obligation_english="Under k > 0, k x² / 2 is greater than or equal to zero for every real displacement x.",
        expected_verdict="ACCEPTED",
        expected_label="Accepted",
        guarantee_level="SMT_RELATIVE",
        limitations="Does not prove that physical springs obey Hooke's law. Educational model only.",
        variables_explained=[
            {"name": "k", "meaning": "spring constant", "unit": "N/m"},
            {"name": "x", "meaning": "displacement", "unit": "m"},
        ],
        equations=[
            _eq(
                r"U = \frac{1}{2} k x^2",
                "U = (1/2) k x^2",
                "<math display='block'><mi>U</mi><mo>=</mo><mfrac><mn>1</mn><mn>2</mn></mfrac>"
                "<mi>k</mi><msup><mi>x</mi><mn>2</mn></msup></math>",
                "Declared elastic potential in one dimension.",
            )
        ],
        charts=[
            {
                "id": "spring-vs-x",
                "kind": "quadratic",
                "role": "illustrative",
                "title": "Spring energy versus displacement",
                "subtitle": "Illustrative U = ½ k x² for k = 2 N/m. Not a verified plot.",
                "x_label": "x (m)",
                "y_label": "U (J)",
                "samples": [{"x": str(x), "U": str(x * x)} for x in range(-4, 5)],
            }
        ],
        submission=_sub(
            "Spring potential energy",
            r"U = \frac{1}{2} k x^2 \geq 0,\quad k>0",
            {"k": {"dimension": K}, "x": {"dimension": L}},
            [{"lhs": "k", "op": ">", "rhs": "0"}],
            [_rel("spring-energy", "k*x**2/2", ">=", "0")],
        ),
        related=["inv-01-kinetic", "inv-05-oscillator"],
        source_ids=["src-mit-ocw-801sc", "src-natalia-maintainers"],
        capability="runnable",
        expected_by_mode={
            "fast": "ACCEPTED",
            "certified": "KERNEL_CHECKED if the polynomial fragment covers the square",
            "lean": "ABSTAIN (dimensioned reals)",
        },
    ),
    _inv(
        id="inv-05-oscillator",
        example_id=None,
        title="Undamped harmonic oscillator energy",
        domain="Classical Mechanics",
        difficulty="Intermediate",
        tier=2,
        learning_minutes=7,
        question="Under the model assumptions, how is total mechanical energy represented?",
        why_it_matters=(
            "Adding two non-negative quadratic terms yields a non-negative energy expression. "
            "That is not a proof that energy is conserved along trajectories of the ODE."
        ),
        model=(
            "One-dimensional harmonic oscillator with m > 0 and k > 0. Total energy is declared as "
            "½ k x² + ½ m v². No time derivative or flow is encoded."
        ),
        obligation_english=(
            "Under m > 0 and k > 0, the declared sum ½ k x² + ½ m v² is greater than or equal to zero."
        ),
        expected_verdict="ACCEPTED",
        expected_label="Accepted",
        guarantee_level="SMT_RELATIVE",
        limitations=(
            "NatalIA verifies the algebraic sign of the declared energy expression. "
            "It does not formalize ẍ = −(k/m) x, conservation along solutions, or uniqueness of motion."
        ),
        variables_explained=[
            {"name": "m", "meaning": "mass", "unit": "kg"},
            {"name": "k", "meaning": "spring constant", "unit": "N/m"},
            {"name": "x", "meaning": "displacement", "unit": "m"},
            {"name": "v", "meaning": "velocity", "unit": "m/s"},
        ],
        equations=[
            _eq(
                r"E = \frac{1}{2} k x^2 + \frac{1}{2} m v^2",
                "E = (1/2) k x^2 + (1/2) m v^2",
                "<math display='block'><mi>E</mi><mo>=</mo><mfrac><mn>1</mn><mn>2</mn></mfrac>"
                "<mi>k</mi><msup><mi>x</mi><mn>2</mn></msup><mo>+</mo><mfrac><mn>1</mn><mn>2</mn></mfrac>"
                "<mi>m</mi><msup><mi>v</mi><mn>2</mn></msup></math>",
                "Declared mechanical energy. Not a dynamical certificate.",
            )
        ],
        charts=[],
        planned=["ODE encoding", "conservation along solutions"],
        submission=_sub(
            "Undamped oscillator energy expression",
            r"E=\frac12 k x^2+\frac12 m v^2\geq 0,\quad m>0,\,k>0",
            {"m": {"dimension": M}, "k": {"dimension": K}, "x": {"dimension": L}, "v": {"dimension": V}},
            [{"lhs": "m", "op": ">", "rhs": "0"}, {"lhs": "k", "op": ">", "rhs": "0"}],
            [_rel("mechanical-energy", "k*x**2/2 + m*v**2/2", ">=", "0")],
        ),
        related=["inv-04-spring", "inv-10-damped"],
        source_ids=["src-mit-ocw-801sc", "src-natalia-maintainers"],
        capability="runnable",
        expected_by_mode={"fast": "ACCEPTED", "certified": "fragment-dependent", "lean": "ABSTAIN"},
    ),
    _inv(
        id="inv-06-rc",
        example_id=None,
        title="RC circuit time-constant dimensions",
        domain="Circuits",
        difficulty="Intermediate",
        tier=2,
        learning_minutes=6,
        question="Does V(t)=V₀(1−e^{−t/RC}) have dimensionally valid terms?",
        why_it_matters=(
            "The argument of an exponential must be dimensionless. That requires t and RC to share time dimension."
        ),
        model=(
            "Series RC charging from a constant voltage V₀. Resistance and capacitance use SI base dimensions. "
            "The exponential waveform plotted below is an illustrative model, not a verified ODE solution."
        ),
        obligation_english=(
            "Under t ≥ 0, R > 0 and C > 0, the ratio t/(R C) is a well-formed dimensionless quantity "
            "and is greater than or equal to zero. NatalIA does not prove the charging ODE."
        ),
        expected_verdict="ACCEPTED",
        expected_label="Accepted",
        guarantee_level="SMT_RELATIVE",
        limitations=(
            "The exponential charging formula is not sent to the SMT adapter (transcendentals are unsupported there). "
            "The verified obligation is only the sign and dimensional legality of t/(R C)."
        ),
        variables_explained=[
            {"name": "t", "meaning": "time", "unit": "s"},
            {"name": "R", "meaning": "resistance", "unit": "Ω"},
            {"name": "C", "meaning": "capacitance", "unit": "F"},
        ],
        equations=[
            _eq(
                r"V(t)=V_0\bigl(1-e^{-t/RC}\bigr)",
                "V(t) = V0 (1 - exp(-t/(R C)))",
                "<math display='block'><mi>V</mi><mo>(</mo><mi>t</mi><mo>)</mo><mo>=</mo>"
                "<msub><mi>V</mi><mn>0</mn></msub><mo>(</mo><mn>1</mn><mo>−</mo>"
                "<msup><mi>e</mi><mrow><mo>−</mo><mi>t</mi><mo>/</mo><mi>R</mi><mi>C</mi></mrow></msup>"
                "<mo>)</mo></math>",
                "Illustrative charging formula. The solver obligation below is only t/(R C) ≥ 0.",
            )
        ],
        charts=[
            {
                "id": "rc-charge",
                "kind": "series",
                "role": "illustrative",
                "title": "Illustrative RC charging curve",
                "subtitle": "Educational sketch with τ = RC = 1. Not generated from a verified differential equation.",
                "x_label": "t / τ",
                "y_label": "V / V₀",
                "samples": [
                    {"t": "0", "V": "0"},
                    {"t": "0.5", "V": "0.393"},
                    {"t": "1", "V": "0.632"},
                    {"t": "2", "V": "0.865"},
                    {"t": "3", "V": "0.950"},
                    {"t": "4", "V": "0.982"},
                    {"t": "5", "V": "0.993"},
                ],
            }
        ],
        submission=_sub(
            "RC time-constant dimensions",
            r"t \ge 0,\, R>0,\, C>0 \implies t/(RC) \ge 0",
            {"t": {"dimension": T}, "R": {"dimension": OHM}, "C": {"dimension": FARAD}},
            [
                {"lhs": "t", "op": ">=", "rhs": "0"},
                {"lhs": "R", "op": ">", "rhs": "0"},
                {"lhs": "C", "op": ">", "rhs": "0"},
            ],
            [_rel("dimensionless-time", "t/(R*C)", ">=", "0")],
        ),
        related=["inv-03-dimensions"],
        planned=["Formalization of the charging ODE", "SMT support for exp"],
        source_ids=["src-bipm-si-brochure", "src-natalia-maintainers"],
        capability="runnable",
        expected_by_mode={"fast": "ACCEPTED", "certified": "fragment-dependent", "lean": "ABSTAIN"},
    ),
    _inv(
        id="inv-07-rational-limit",
        example_id="04-limit",
        title="Rational limit at infinity",
        domain="Limits",
        difficulty="Advanced",
        tier=3,
        learning_minutes=5,
        question="Is the limit of (2x²+1)/(x²+3) as x → +∞ equal to 2?",
        why_it_matters="Symbolic limits can agree with the expected value and still remain advisory.",
        model="Local CAS adapter over rational expressions. Infinity is the only implemented target.",
        obligation_english="The declared limit equals 2. The adapter may match 2 and still report unknown status.",
        expected_verdict="ABSTAIN",
        expected_label="Abstain",
        guarantee_level="ADVISORY",
        limitations="Agreement of a CAS result is not a kernel certificate and is not undecidability of analysis.",
        variables_explained=[{"name": "x", "meaning": "real variable", "unit": "dimensionless"}],
        equations=[
            _eq(
                r"\lim_{x\to\infty}\frac{2x^2+1}{x^2+3}=2",
                "lim x→∞ (2x^2+1)/(x^2+3) = 2",
                "<math display='block'><munder><mi>lim</mi><mrow><mi>x</mi><mo>→</mo><mo>∞</mo></mrow></munder>"
                "<mfrac><mrow><mn>2</mn><msup><mi>x</mi><mn>2</mn></msup><mo>+</mo><mn>1</mn></mrow>"
                "<mrow><msup><mi>x</mi><mn>2</mn></msup><mo>+</mo><mn>3</mn></mrow></mfrac><mo>=</mo><mn>2</mn></math>",
                "Advisory CAS obligation.",
            )
        ],
        submission=_sub(
            "Rational limit at infinity",
            r"\lim_{x\to\infty}(2x^2+1)/(x^2+3)=2",
            {"x": {"dimension": ZERO}},
            [],
            [
                {
                    "kind": "limit",
                    "id": "ratio",
                    "expression": "(2*x**2+1)/(x**2+3)",
                    "variable": "x",
                    "target": "infinity",
                    "expected": "2",
                }
            ],
        ),
        related=["inv-08-oscillation"],
        capability="negative_boundary",
        source_ids=["src-natalia-maintainers"],
        expected_by_mode={"fast": "ABSTAIN", "certified": "ABSTAIN", "lean": "ABSTAIN"},
    ),
    _inv(
        id="inv-08-oscillation",
        example_id="09-oscillation",
        title="Oscillatory limit",
        domain="Limits",
        difficulty="Advanced",
        tier=3,
        learning_minutes=4,
        question="Does the local adapter establish lim sin(x)/x as x → +∞?",
        why_it_matters="Principled abstention when the expression leaves the supported fragment.",
        model="The asymptotic adapter accepts rational expressions and exp, not sin.",
        obligation_english="The declared oscillatory limit is established by the local adapter.",
        expected_verdict="ABSTAIN",
        expected_label="Abstain",
        guarantee_level="ADVISORY",
        limitations=(
            "Classical analysis treats this limit; NatalIA does not implement that theory. "
            "Abstention is a fragment boundary, not a claim of undecidability."
        ),
        variables_explained=[{"name": "x", "meaning": "real variable", "unit": "dimensionless"}],
        equations=[
            _eq(
                r"\lim_{x\to\infty}\frac{\sin x}{x}=0",
                "lim x→∞ sin(x)/x = 0",
                "<math display='block'><munder><mi>lim</mi><mrow><mi>x</mi><mo>→</mo><mo>∞</mo></mrow></munder>"
                "<mfrac><mrow><mi>sin</mi><mo>(</mo><mi>x</mi><mo>)</mo></mrow><mi>x</mi></mfrac>"
                "<mo>=</mo><mn>0</mn></math>",
                "Outside the supported CAS fragment.",
            )
        ],
        submission=_sub(
            "Oscillatory limit",
            r"\lim_{x\to\infty}\sin(x)/x",
            {"x": {"dimension": ZERO}},
            [],
            [
                {
                    "kind": "limit",
                    "id": "osc",
                    "expression": "sin(x)/x",
                    "variable": "x",
                    "target": "infinity",
                    "expected": "0",
                }
            ],
        ),
        related=["inv-07-rational-limit"],
        capability="negative_boundary",
        source_ids=["src-natalia-maintainers"],
        expected_by_mode={"fast": "ABSTAIN", "certified": "ABSTAIN", "lean": "ABSTAIN"},
    ),
    _inv(
        id="inv-09-domain",
        example_id="07-singularity",
        title="Division and domain safety",
        domain="Mathematics",
        difficulty="Advanced",
        tier=3,
        learning_minutes=6,
        question="When does x/x = 1 hold, and why does missing x ≠ 0 matter?",
        why_it_matters=(
            "Cancellation looks obvious until zero is allowed. NatalIA does not silently totalize division."
        ),
        model="Real arithmetic with explicit domain restrictions as assumptions. Two companion formalizations.",
        obligation_english=(
            "This page runs the unrestricted claim x/x = 1. The companion with x ≠ 0 is offered as a next action."
        ),
        expected_verdict="ABSTAIN",
        expected_label="Abstain",
        guarantee_level="SMT_RELATIVE",
        limitations="Does not develop distribution theory or removable discontinuities beyond the declared encoding.",
        variables_explained=[{"name": "x", "meaning": "real variable", "unit": "dimensionless"}],
        charts=[
            {
                "id": "division-hole",
                "kind": "quadratic",
                "role": "illustrative",
                "title": "Domain restriction near division by zero",
                "subtitle": "Illustrative samples of x/x away from zero. The hole at x = 0 is the modelling point, not a plotted proof.",
                "x_label": "x",
                "y_label": "x/x",
                "samples": [
                    {"x": str(x), "y": "1"} for x in [-3, -2, -1, 1, 2, 3]
                ],
            }
        ],
        equations=[
            _eq(
                r"x/x = 1",
                "x/x = 1",
                "<math display='block'><mi>x</mi><mo>/</mo><mi>x</mi><mo>=</mo><mn>1</mn></math>",
                "Unrestricted form. Expected abstention.",
            ),
            _eq(
                r"x\neq 0 \implies x/x = 1",
                "x != 0 implies x/x = 1",
                "<math display='block'><mi>x</mi><mo>≠</mo><mn>0</mn><mo>⇒</mo>"
                "<mi>x</mi><mo>/</mo><mi>x</mi><mo>=</mo><mn>1</mn></math>",
                "Companion with explicit domain. Expected SMT-relative acceptance if you load that template.",
            ),
        ],
        companion_submission=_sub(
            "x/x == 1 with x != 0",
            r"x\neq 0 \implies x/x = 1",
            {"x": {"dimension": ZERO}},
            [{"lhs": "x", "op": "!=", "rhs": "0"}],
            [_rel("cancel", "x/x", "==", "1")],
        ),
        submission=_sub(
            "x/x == 1 without domain",
            r"x/x = 1",
            {"x": {"dimension": ZERO}},
            [],
            [_rel("cancel", "x/x", "==", "1")],
        ),
        related=["inv-02-counterexample", "inv-12-domain-restored"],
        capability="negative_boundary",
        source_ids=["src-natalia-maintainers"],
        expected_by_mode={"fast": "ABSTAIN", "certified": "ABSTAIN", "lean": "ABSTAIN"},
    ),
    _inv(
        id="inv-10-damped",
        example_id=None,
        title="Damped oscillator energy dissipation",
        domain="Classical Mechanics",
        difficulty="Research Boundary",
        tier=4,
        learning_minutes=8,
        question="Does a linear damper dissipate mechanical energy, and what can NatalIA currently check?",
        why_it_matters=(
            "Energy decay is a standard Lyapunov story. The laboratory can check an algebraic sign, "
            "not the chain rule along an ODE."
        ),
        model=(
            "Target identity from classical mechanics: dE/dt = −c v² ≤ 0 for c ≥ 0. "
            "NatalIA has no derivative operator in the DSL, so the dynamical claim is an explicit proof hole."
        ),
        obligation_english=(
            "The dynamical statement dE/dt = −c v² is not encoded. The submitted obligation is a declared proof hole. "
            "The algebraic comparison −c v² ≤ 0 under c ≥ 0 is illustrated, not submitted as a stand-in proof of dissipation."
        ),
        expected_verdict="ABSTAIN",
        expected_label="Abstain",
        guarantee_level="ADVISORY",
        limitations=(
            "Illustrative derivation only. Formal obligation currently supported: none for dE/dt. "
            "Required extensions: time derivatives, chain rule, and a trajectory semantics."
        ),
        variables_explained=[
            {"name": "c", "meaning": "damping coefficient", "unit": "N·s/m"},
            {"name": "v", "meaning": "velocity", "unit": "m/s"},
        ],
        equations=[
            _eq(
                r"\frac{dE}{dt} = -c v^2 \le 0",
                "dE/dt = -c v^2 <= 0",
                "<math display='block'><mfrac><mrow><mi>d</mi><mi>E</mi></mrow><mrow><mi>d</mi><mi>t</mi></mrow></mfrac>"
                "<mo>=</mo><mo>−</mo><mi>c</mi><msup><mi>v</mi><mn>2</mn></msup><mo>≤</mo><mn>0</mn></math>",
                "Model target. Not a currently certified dynamical theorem.",
            )
        ],
        charts=[
            {
                "id": "damped-energy",
                "kind": "series",
                "role": "illustrative",
                "title": "Illustrative undamped versus damped energy",
                "subtitle": "Sketches, not solutions of a verified ODE. Do not read them as KERNEL_CHECKED trajectories.",
                "x_label": "t (arbitrary)",
                "y_label": "E (arbitrary)",
                "series": [
                    {
                        "name": "undamped (illustrative)",
                        "samples": [
                            {"t": "0", "E": "1"},
                            {"t": "1", "E": "1"},
                            {"t": "2", "E": "1"},
                            {"t": "3", "E": "1"},
                            {"t": "4", "E": "1"},
                        ],
                    },
                    {
                        "name": "damped (illustrative)",
                        "samples": [
                            {"t": "0", "E": "1"},
                            {"t": "1", "E": "0.61"},
                            {"t": "2", "E": "0.37"},
                            {"t": "3", "E": "0.22"},
                            {"t": "4", "E": "0.14"},
                        ],
                    },
                ],
            }
        ],
        planned=["Time derivatives in the DSL", "Lyapunov decrease along flows", "Certified dissipation"],
        submission=_sub(
            "Damped oscillator energy dissipation (planned)",
            r"dE/dt = -c v^2 \le 0 \text{ is not encoded}",
            {"c": {"dimension": DAMPING}, "v": {"dimension": V}},
            [{"lhs": "c", "op": ">=", "rhs": "0"}],
            [
                {
                    "kind": "proof_hole",
                    "id": "energy-dissipation",
                    "description": "dE/dt = -c v^2 is not in the supported DSL; dynamical proof is planned.",
                }
            ],
        ),
        related=["inv-05-oscillator", "inv-15-int-square"],
        capability="educational_unverified",
        source_ids=["src-mit-ocw-801sc", "src-lean-tpil4-axioms", "src-natalia-maintainers"],
        expected_by_mode={
            "fast": "ABSTAIN",
            "certified": "ABSTAIN",
            "lean": "ABSTAIN for dE/dt; companion algebraic Int lemma is a separate investigation",
        },
    ),
    _inv(
        id="inv-11-contradiction",
        example_id="06-contradiction",
        title="Why contradictory assumptions must not yield acceptance",
        domain="Logic",
        difficulty="Foundations",
        tier=1,
        learning_minutes=5,
        educational_objective="vacuity-guard",
        question="If the assumptions cannot all be true, should a wild claim be accepted?",
        why_it_matters=(
            "From false premises anything follows. NatalIA refuses to treat an empty model as a successful proof."
        ),
        model="Two mutually exclusive assumptions on a single real variable, plus an unrelated equality claim.",
        obligation_english=(
            "Under x > 1 and x < 0, the claim x == 42 is accepted. The laboratory must not grant that acceptance."
        ),
        expected_verdict="ABSTAIN",
        expected_label="Abstain",
        guarantee_level="ADVISORY",
        limitations="This is a vacuity guard, not a general first-order consistency checker.",
        variables_explained=[{"name": "x", "meaning": "real variable", "unit": "dimensionless"}],
        equations=[
            _eq(
                r"x>1 \land x<0 \implies x=42",
                "x > 1 and x < 0 imply x = 42",
                "<math display='block'><mi>x</mi><mo>&gt;</mo><mn>1</mn><mo>∧</mo><mi>x</mi>"
                "<mo>&lt;</mo><mn>0</mn><mo>⇒</mo><mi>x</mi><mo>=</mo><mn>42</mn></math>",
                "Vacuous implication. Must not be reported as a successful theorem.",
            )
        ],
        submission=_sub(
            "Contradictory assumptions",
            r"x>1 \land x<0 \implies x=42",
            {"x": {"dimension": ZERO}},
            [{"lhs": "x", "op": ">", "rhs": "1"}, {"lhs": "x", "op": "<", "rhs": "0"}],
            [_rel("vacuous", "x", "==", "42")],
        ),
        related=["inv-02-counterexample"],
        capability="negative_boundary",
        source_ids=["src-natalia-maintainers"],
        expected_by_mode={"fast": "ABSTAIN", "certified": "ABSTAIN", "lean": "ABSTAIN"},
    ),
    _inv(
        id="inv-12-domain-restored",
        example_id="08-domain-fixed",
        title="Division after restoring x ≠ 0",
        domain="Mathematics",
        difficulty="Foundations",
        tier=1,
        learning_minutes=4,
        question="Does adding the missing domain restriction x ≠ 0 allow x/x = 1?",
        why_it_matters="The unrestricted companion abstains. This page restores the hypothesis instead of silently cancelling.",
        model="Real arithmetic with an explicit inequality assumption excluding zero.",
        obligation_english="Under x ≠ 0, x/x equals 1.",
        expected_verdict="ACCEPTED",
        expected_label="Accepted",
        guarantee_level="SMT_RELATIVE",
        limitations="Acceptance is SMT-relative. Removable discontinuities in analysis are not formalized.",
        variables_explained=[{"name": "x", "meaning": "real variable", "unit": "dimensionless"}],
        equations=[
            _eq(
                r"x\neq 0 \implies x/x = 1",
                "x != 0 implies x/x = 1",
                "<math display='block'><mi>x</mi><mo>≠</mo><mn>0</mn><mo>⇒</mo>"
                "<mi>x</mi><mo>/</mo><mi>x</mi><mo>=</mo><mn>1</mn></math>",
                "Domain restored. Companion of inv-09-domain.",
            )
        ],
        submission=_sub(
            "x/x == 1 with x != 0",
            r"x\neq 0 \implies x/x = 1",
            {"x": {"dimension": ZERO}},
            [{"lhs": "x", "op": "!=", "rhs": "0"}],
            [_rel("cancel", "x/x", "==", "1")],
        ),
        related=["inv-09-domain"],
        capability="runnable",
        source_ids=["src-natalia-maintainers"],
        expected_by_mode={"fast": "ACCEPTED", "certified": "fragment-dependent", "lean": "ABSTAIN"},
        common_mistakes=["Cancelling x/x without stating x ≠ 0"],
        variation="Remove the assumption and compare with inv-09-domain.",
    ),
    _inv(
        id="inv-13-electrical-power",
        example_id=None,
        title="Electrical power sign under declared restrictions",
        domain="Circuits",
        difficulty="Intermediate",
        tier=2,
        learning_minutes=5,
        question="If voltage and current are declared nonnegative, is instantaneous power P = V I nonnegative?",
        why_it_matters="Sign of electrical power depends on the declared orientation and restrictions, not on a hidden convention.",
        model=(
            "Lumped DC model P = V I with SI dimensions. Passive sign convention is an assumption, not a measurement. "
            "AC, RMS, and three-phase power are out of scope."
        ),
        obligation_english="Under V ≥ 0 and I ≥ 0, the product V I is greater than or equal to zero.",
        expected_verdict="ACCEPTED",
        expected_label="Accepted",
        guarantee_level="SMT_RELATIVE",
        limitations="Does not prove circuit laws or that a physical source obeys the sign convention.",
        variables_explained=[
            {"name": "V", "meaning": "voltage", "unit": "V"},
            {"name": "I", "meaning": "current", "unit": "A"},
        ],
        equations=[
            _eq(
                r"P = V I \ge 0",
                "P = V I >= 0",
                "<math display='block'><mi>P</mi><mo>=</mo><mi>V</mi><mi>I</mi><mo>≥</mo><mn>0</mn></math>",
                "Declared instantaneous power under nonnegative V and I.",
            )
        ],
        submission=_sub(
            "Nonnegative electrical power under V>=0, I>=0",
            r"V\ge 0,\, I\ge 0 \implies V I \ge 0",
            {"V": {"dimension": VOLT}, "I": {"dimension": AMP}},
            [{"lhs": "V", "op": ">=", "rhs": "0"}, {"lhs": "I", "op": ">=", "rhs": "0"}],
            [_rel("electrical-power", "V*I", ">=", "0")],
        ),
        related=["inv-06-rc"],
        capability="runnable",
        source_ids=["src-bipm-si-brochure", "src-natalia-maintainers"],
        expected_by_mode={"fast": "ACCEPTED", "certified": "fragment-dependent", "lean": "ABSTAIN (dimensioned reals)"},
        application_context="DC resistor with declared polarity.",
        common_mistakes=["Treating generator convention as the same obligation without restating signs"],
    ),
    _inv(
        id="inv-14-interval-box",
        example_id=None,
        title="Exact interval containment on a declared box",
        domain="Limits",
        difficulty="Intermediate",
        tier=2,
        learning_minutes=5,
        question="On the box x ∈ [0, 1], is x² ≤ 1 guaranteed by the interval adapter?",
        why_it_matters="A sound enclosure can confirm a relation on a box without being a global real-line certificate.",
        model="Exact rational endpoint arithmetic on a closed box. Overlapping intervals are not treated as proof of containment beyond the enclosure test.",
        obligation_english="For every x in [0, 1], x² ≤ 1. Fast mode may accept globally; the interval adapter reports enclosure on the box only.",
        expected_verdict="ACCEPTED",
        expected_label="Accepted",
        guarantee_level="SMT_RELATIVE",
        limitations=(
            "The interval adapter currently records a consistent enclosure as unknown/not a global certificate. "
            "SMT-relative acceptance of x² ≤ 1 is a different guarantee. Sampling plots are not the proof."
        ),
        variables_explained=[{"name": "x", "meaning": "real variable restricted to a box", "unit": "dimensionless"}],
        equations=[
            _eq(
                r"x\in[0,1]\implies x^2\le 1",
                "x in [0,1] implies x^2 <= 1",
                "<math display='block'><mi>x</mi><mo>∈</mo><mo>[</mo><mn>0</mn><mo>,</mo><mn>1</mn><mo>]</mo>"
                "<mo>⇒</mo><msup><mi>x</mi><mn>2</mn></msup><mo>≤</mo><mn>1</mn></math>",
                "Box claim. Interval enclosure is independent of SMT.",
            )
        ],
        charts=[
            {
                "id": "box-square",
                "kind": "quadratic",
                "role": "illustrative",
                "visual_class": "numerical_approximation",
                "title": "x² on [0,1] versus the bound 1",
                "subtitle": "Illustration. Exact endpoints are 0 and 1; the SMT claim is x² ≤ 1 on the reals with the declared box.",
                "x_label": "x",
                "y_label": "x²",
                "samples": [{"x": str(i / 4), "y": str((i / 4) ** 2)} for i in range(0, 5)],
            }
        ],
        submission=_sub(
            "x**2 <= 1 on [0,1]",
            r"x\in[0,1]\implies x^2\le 1",
            {"x": {"dimension": ZERO, "domain_min": "0", "domain_max": "1"}},
            [],
            [_rel("box-square", "x**2", "<=", "1")],
        ),
        related=["inv-02-counterexample"],
        capability="runnable",
        source_ids=["src-natalia-maintainers"],
        expected_by_mode={
            "fast": "ACCEPTED",
            "certified": "fragment-dependent",
            "lean": "ABSTAIN",
        },
        common_mistakes=["Treating a plot sample as interval containment"],
    ),
    _inv(
        id="inv-15-int-square",
        example_id=None,
        title="Integer square non-negativity (Lean fragment)",
        domain="Mathematics",
        difficulty="Foundations",
        tier=1,
        learning_minutes=4,
        question="Over integers, is n² nonnegative, and can NatalIA ask Lean rather than SMT?",
        why_it_matters="This is the only current payload that maps onto the pinned Lean integer fragment.",
        model=(
            "Dimensionless variable n. The Lean certificate interprets n as Int. "
            "That is a different statement from the default real SMT encoding."
        ),
        obligation_english="n * n ≥ 0 for the integer image of this dimensionless template.",
        expected_verdict="ACCEPTED",
        expected_label="Accepted",
        guarantee_level="SMT_RELATIVE",
        limitations=(
            "Fast mode uses SMT over reals. Lean mode requires the pinned toolchain; if Lean is missing, "
            "the result is ABSTAIN/UNAVAILABLE, never a silent SMT accept."
        ),
        variables_explained=[{"name": "n", "meaning": "integer (Lean) / real (Fast)", "unit": "dimensionless"}],
        equations=[
            _eq(
                r"n^2 \ge 0",
                "n^2 >= 0",
                "<math display='block'><msup><mi>n</mi><mn>2</mn></msup><mo>≥</mo><mn>0</mn></math>",
                "Template for lean4_int_poly_pos_v1.",
            )
        ],
        submission=_sub(
            "Integer square non-negativity",
            r"n^2 \ge 0",
            {"n": {"dimension": ZERO}},
            [],
            [_rel("int-square", "n*n", ">=", "0")],
        ),
        related=["inv-10-damped"],
        capability="runnable",
        source_ids=["src-lean-tpil4-axioms", "src-natalia-maintainers"],
        expected_by_mode={
            "fast": "ACCEPTED",
            "certified": "KERNEL_CHECKED if natalia.kernel covers the polynomial",
            "lean": "ACCEPTED only if lake/lean checks NatalIA.int_sq_nonneg; else ABSTAIN",
        },
        content_review="maintainer-reviewed-v1.1",
    ),
]


def list_investigations():
    return {
        "schema": SCHEMA,
        "content_version": CONTENT_VERSION,
        "count": len(INVESTIGATIONS),
        "domains": sorted({item["domain"] for item in INVESTIGATIONS}),
        "difficulties": ["Foundations", "Intermediate", "Advanced", "Research Boundary"],
        "capabilities": sorted({item.get("capability", "runnable") for item in INVESTIGATIONS}),
        "items": INVESTIGATIONS,
    }


def get_investigation(ident: str):
    for item in INVESTIGATIONS:
        if item["id"] == ident:
            return item
    return None

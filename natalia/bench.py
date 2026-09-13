"""PhysVerifyBench v0.1: template families with independent labels, split by family.

This is a public regression/evaluation set in the same repository. It is not a hidden
holdout. Labels of system behavior are justified by the template, then checked by the
local pipeline. Mathematical validity is recorded separately and is never taken from
the solver under test as the only source of truth.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

from natalia.engine import verify
from natalia.models import Submission

VERSION = "physverifybench-v0.1"
ZERO = ["0"] * 7
M = ["1", "0", "0", "0", "0", "0", "0"]
V = ["0", "1", "-1", "0", "0", "0", "0"]
E = ["1", "2", "-2", "0", "0", "0", "0"]
P = ["1", "1", "-1", "0", "0", "0", "0"]


def _rel(lhs, op, rhs, ident="claim"):
    return {"kind": "relation", "id": ident, "lhs": lhs, "op": op, "rhs": rhs}


def _payload(title, variables, assumptions, claims):
    return {
        "schema_version": "1.0",
        "title": title,
        "source_latex": "",
        "variables": variables,
        "assumptions": assumptions,
        "claims": claims,
        "budget_ms": 4000,
    }


def _item(family, ident, split, math_status, system_expected, evidence, origin, payload, notes=""):
    Submission.model_validate(payload)
    return {
        "id": ident,
        "family": family,
        "split": split,
        "mathematical_status": math_status,
        "system_expected": system_expected,
        "expected_evidence": evidence,
        "label_origin": origin,
        "notes": notes,
        "submission": payload,
    }


def build_instances():
    items = []

    # Family squares: even powers are nonnegative (math true / SMT accept).
    for n in range(1, 5):
        split = "dev" if n <= 4 else "val" if n <= 6 else "test"
        items.append(
            _item(
                "even_powers_nonneg",
                f"even-pow-{n}",
                split,
                "true",
                "ACCEPTED",
                "smt_relative",
                "Polynomial identity: even integer power is a square.",
                _payload(
                    f"x**{2 * n} >= 0",
                    {"x": {"dimension": ZERO}},
                    [],
                    [_rel(f"x**{2 * n}", ">=", "0")],
                ),
            )
        )

    for k in range(0, 12):
        split = "dev" if k <= 5 else "val" if k <= 8 else "test"
        items.append(
            _item(
                "shifted_nonneg_constant",
                f"sq-plus-{k}",
                split,
                "true",
                "ACCEPTED",
                "smt_relative",
                "x^2 + k >= k for k>=0 follows from x^2 >= 0.",
                _payload(
                    f"x**2 + {k} >= {k}",
                    {"x": {"dimension": ZERO}},
                    [],
                    [_rel(f"x**2 + {k}", ">=", str(k))],
                ),
            )
        )

    # Shifted squares with distinct constants.
    for a in range(-6, 7):
        if a == 0:
            continue
        split = "dev" if abs(a) <= 3 else "val" if abs(a) <= 5 else "test"
        items.append(
            _item(
                "shifted_squares",
                f"shift-sq-{a}",
                split,
                "true",
                "ACCEPTED",
                "smt_relative",
                "Square of (x-a) is nonnegative for every real a.",
                _payload(
                    f"(x-({a}))**2 >= 0",
                    {"x": {"dimension": ZERO}},
                    [],
                    [_rel(f"(x-({a}))**2", ">=", "0")],
                ),
            )
        )

    # False lower bounds on squares.
    for k in range(1, 9):
        split = "dev" if k <= 4 else "val" if k <= 6 else "test"
        items.append(
            _item(
                "square_false_floor",
                f"sq-ge-{k}",
                split,
                "false",
                "REFUTED",
                "exact_rational_witness",
                "x=0 is a counterexample to x^2 >= k for k>0.",
                _payload(
                    f"x**2 >= {k}",
                    {"x": {"dimension": ZERO}},
                    [],
                    [_rel("x**2", ">=", str(k))],
                ),
            )
        )

    # Linear claims without domain.
    for k in range(-4, 6):
        split = "dev" if k <= 0 else "val" if k <= 3 else "test"
        items.append(
            _item(
                "unrestricted_linear",
                f"x-ge-{k}",
                split,
                "false",
                "REFUTED",
                "exact_rational_witness",
                "An unrestricted linear inequality over the reals is false.",
                _payload(
                    f"x >= {k}",
                    {"x": {"dimension": ZERO}},
                    [],
                    [_rel("x", ">=", str(k))],
                ),
            )
        )

    # Identities (x+a)^2 expansion.
    for a in range(1, 9):
        split = "dev" if a <= 4 else "val" if a <= 6 else "test"
        items.append(
            _item(
                "binomial_identity",
                f"bin-{a}",
                split,
                "true",
                "ACCEPTED",
                "smt_relative",
                "Algebraic expansion of (x+a)^2.",
                _payload(
                    f"(x+{a})**2 == x**2 + {2 * a}*x + {a * a}",
                    {"x": {"dimension": ZERO}},
                    [],
                    [_rel(f"(x+{a})**2", "==", f"x**2 + {2 * a}*x + {a * a}")],
                ),
            )
        )
        items.append(
            _item(
                "binomial_false",
                f"bin-false-{a}",
                split,
                "false",
                "REFUTED",
                "exact_rational_witness",
                "Wrong cross term: 2a replaced by 2a+1.",
                _payload(
                    f"(x+{a})**2 == x**2 + {2 * a + 1}*x + {a * a}",
                    {"x": {"dimension": ZERO}},
                    [],
                    [_rel(f"(x+{a})**2", "==", f"x**2 + {2 * a + 1}*x + {a * a}")],
                ),
            )
        )

    # Domain / singularity pairs at distinct poles x=a.
    for a in range(-3, 4):
        split = "dev" if abs(a) <= 1 else "val" if abs(a) == 2 else "test"
        expr = f"(x-({a}))/(x-({a}))"
        items.append(
            _item(
                "pole_unrestricted",
                f"pole-open-{a}",
                split,
                "false",
                "ABSTAIN",
                "smt_relative",
                "Identity fails at the pole; adapter abstains without a domain guard.",
                _payload(
                    f"{expr} == 1",
                    {"x": {"dimension": ZERO}},
                    [],
                    [_rel(expr, "==", "1")],
                ),
                notes="Mathematically false at x=a; system must not accept.",
            )
        )
        items.append(
            _item(
                "pole_excluded",
                f"pole-closed-{a}",
                split,
                "true_on_domain",
                "ACCEPTED",
                "smt_relative",
                "With x≠a the rational identity holds on the declared domain.",
                _payload(
                    f"x != {a} => {expr} == 1",
                    {"x": {"dimension": ZERO}},
                    [{"lhs": "x", "op": "!=", "rhs": str(a)}],
                    [_rel(expr, "==", "1")],
                ),
            )
        )

    # Contradictory premises: x>a and x<a.
    for a in range(-3, 5):
        split = "dev" if a <= 0 else "val" if a <= 2 else "test"
        items.append(
            _item(
                "contradictory_bounds",
                f"contra-{a}",
                split,
                "premises_unsat",
                "ABSTAIN",
                "smt_relative",
                "Inconsistent linear bounds; vacuous acceptance is forbidden.",
                _payload(
                    f"x>{a} and x<{a}",
                    {"x": {"dimension": ZERO}},
                    [
                        {"lhs": "x", "op": ">", "rhs": str(a)},
                        {"lhs": "x", "op": "<", "rhs": str(a)},
                    ],
                    [_rel("x**2", ">=", "0")],
                ),
            )
        )

    # Restricted true/false x^2 >= b*x.
    for b in range(1, 7):
        split = "dev" if b <= 3 else "val" if b <= 5 else "test"
        items.append(
            _item(
                "restricted_quadratic_true",
                f"quad-true-{b}",
                split,
                "true_on_domain",
                "ACCEPTED",
                "smt_relative",
                "On x>=b, x(x-b)>=0.",
                _payload(
                    f"x>={b} => x**2 >= {b}*x",
                    {"x": {"dimension": ZERO}},
                    [{"lhs": "x", "op": ">=", "rhs": str(b)}],
                    [_rel("x**2", ">=", f"{b}*x")],
                ),
            )
        )
        items.append(
            _item(
                "restricted_quadratic_false",
                f"quad-false-{b}",
                split,
                "false",
                "REFUTED",
                "exact_rational_witness",
                "On x>=0 the interval (0,b) still refutes x^2 >= b x.",
                _payload(
                    f"x>=0 => x**2 >= {b}*x",
                    {"x": {"dimension": ZERO}},
                    [{"lhs": "x", "op": ">=", "rhs": "0"}],
                    [_rel("x**2", ">=", f"{b}*x")],
                ),
            )
        )

    # Dimensional mismatches with distinct SI pairs.
    mixes = [
        ("mass", M, "time", ["0", "0", "1", "0", "0", "0", "0"]),
        ("energy", E, "momentum", P),
        ("mass", M, "length", ["0", "1", "0", "0", "0", "0", "0"]),
        ("velocity", V, "time", ["0", "0", "1", "0", "0", "0", "0"]),
        ("energy", E, "mass", M),
        ("momentum", P, "length", ["0", "1", "0", "0", "0", "0", "0"]),
        ("velocity", V, "mass", M),
        ("energy", E, "time", ["0", "0", "1", "0", "0", "0", "0"]),
    ]
    for index, (n1, d1, n2, d2) in enumerate(mixes):
        split = ["dev", "dev", "dev", "val", "val", "test", "test", "test"][index]
        items.append(
            _item(
                "dimensional_mix",
                f"dim-{n1}-{n2}",
                split,
                "ill_typed",
                "INVALID",
                "static_compile",
                "SI addition requires identical dimensions. Label from algebra, not from Z3.",
                _payload(
                    f"{n1} + {n2}",
                    {"a": {"dimension": d1}, "b": {"dimension": d2}},
                    [],
                    [_rel("a+b", ">=", "0")],
                ),
            )
        )

    # Kinetic energy family with distinct mass lower bounds.
    for scale in range(1, 6):
        split = "dev" if scale <= 2 else "val" if scale <= 4 else "test"
        items.append(
            _item(
                "kinetic_positive_mass",
                f"ke-m-{scale}",
                split,
                "true_on_domain",
                "ACCEPTED",
                "smt_relative",
                "Classical kinetic energy with strictly positive mass. Zero is polymorphic at the relation boundary.",
                _payload(
                    f"{scale}*m*v**2/2 >= 0 with m>0",
                    {"m": {"dimension": M}, "v": {"dimension": V}},
                    [{"lhs": "m", "op": ">", "rhs": "0"}],
                    [_rel(f"{scale}*m*v**2/2", ">=", "0")],
                ),
            )
        )
        items.append(
            _item(
                "kinetic_unsigned_mass",
                f"ke-free-{scale}",
                split,
                "false",
                "REFUTED",
                "exact_rational_witness",
                "Without a mass sign constraint, negative m refutes nonnegativity.",
                _payload(
                    f"unsigned kinetic scaled {scale}",
                    {"m": {"dimension": M}, "v": {"dimension": V}},
                    [],
                    [_rel(f"{scale}*m*v**2", ">=", "0")],
                ),
            )
        )

    # Proof holes with distinct descriptions / companion claims.
    for n in range(1, 7):
        split = "dev" if n <= 3 else "val" if n <= 5 else "test"
        items.append(
            _item(
                "declared_holes",
                f"hole-{n}",
                split,
                "incomplete",
                "ABSTAIN",
                "unavailable",
                "A declared proof hole is open by contract, independent of the solver.",
                _payload(
                    f"hole {n}",
                    {"x": {"dimension": ZERO}},
                    [],
                    [
                        _rel("x**2", ">=", "0", ident="square"),
                        {
                            "kind": "proof_hole",
                            "id": f"gap{n}",
                            "description": f"Missing lemma number {n} in the informal argument.",
                        },
                    ],
                ),
            )
        )

    # Advisory limits with distinct rationals approaching integers.
    for n in range(1, 6):
        split = "dev" if n <= 2 else "val" if n <= 4 else "test"
        items.append(
            _item(
                "advisory_limits",
                f"lim-{n}",
                split,
                "classically_true",
                "ABSTAIN",
                "cas_advisory",
                "CAS may match the expected integer; status remains unknown by contract.",
                _payload(
                    f"limit ( {n}*x**2 + 1 ) / (x**2 + 1 )",
                    {"x": {"dimension": ZERO}},
                    [],
                    [
                        {
                            "kind": "limit",
                            "id": "ratio",
                            "expression": f"({n}*x**2+1)/(x**2+1)",
                            "variable": "x",
                            "target": "infinity",
                            "expected": str(n),
                        }
                    ],
                ),
            )
        )

    # Fragment boundary: exp(x) > n is unsupported.
    for n in range(0, 4):
        split = "dev" if n <= 1 else "val" if n == 2 else "test"
        items.append(
            _item(
                "transcendental_boundary",
                f"exp-gt-{n}",
                split,
                "classically_true" if n == 0 else "classically_false_or_open",
                "ABSTAIN",
                "smt_relative",
                "exp is outside the SMT adapter. Classical truth is not used as system ground truth.",
                _payload(
                    f"exp(x) > {n}",
                    {"x": {"dimension": ZERO}},
                    [],
                    [_rel("exp(x)", ">", str(n))],
                ),
            )
        )

    # Interval boxes: x >= k on [-1,1].
    for k in range(2, 7):
        split = "dev" if k <= 3 else "val" if k <= 5 else "test"
        items.append(
            _item(
                "interval_boxes",
                f"box-ge-{k}",
                split,
                "false",
                "REFUTED",
                "interval_enclosure",
                "On [-1,1], x >= k fails throughout for k>=2. Label from interval arithmetic, not Z3 alone.",
                _payload(
                    f"x in [-1,1] => x >= {k}",
                    {"x": {"dimension": ZERO, "domain_min": "-1", "domain_max": "1"}},
                    [],
                    [_rel("x", ">=", str(k))],
                ),
            )
        )

    # Adversarial: true claim under unsat premises (already similar) plus mixed dims hidden in product.
    for n in range(1, 5):
        split = "dev" if n <= 2 else "val" if n == 3 else "test"
        items.append(
            _item(
                "adversarial_hidden_mix",
                f"adv-mix-{n}",
                split,
                "ill_typed",
                "INVALID",
                "static_compile",
                "Product then addition mixes leftover SI units.",
                _payload(
                    f"m*v**{n} + m",
                    {"m": {"dimension": M}, "v": {"dimension": V}},
                    [{"lhs": "m", "op": ">", "rhs": "0"}],
                    [_rel(f"m*v**{n} + m", ">=", "0")],
                ),
            )
        )

    # Two-variable sum of squares vs false floors.
    for k in range(0, 5):
        split = "dev" if k <= 1 else "val" if k <= 3 else "test"
        expected = "ACCEPTED" if k == 0 else "REFUTED"
        math_status = "true" if k == 0 else "false"
        items.append(
            _item(
                "sum_of_squares",
                f"sumsq-ge-{k}",
                split,
                math_status,
                expected,
                "smt_relative" if k == 0 else "exact_rational_witness",
                "x^2+y^2 >= 0 is true; any positive floor is false at the origin.",
                _payload(
                    f"x**2+y**2 >= {k}",
                    {"x": {"dimension": ZERO}, "y": {"dimension": ZERO}},
                    [],
                    [_rel("x**2 + y**2", ">=", str(k))],
                ),
            )
        )

    for n in range(0, 4):
        split = "dev" if n <= 1 else "val" if n <= 3 else "test"
        items.append(
            _item(
                "odd_powers_nonneg",
                f"odd-pow-{2 * n + 1}",
                split,
                "false",
                "REFUTED",
                "exact_rational_witness",
                "Odd integer powers take negative values; x^{2n+1} >= 0 is false.",
                _payload(
                    f"x**{2 * n + 1} >= 0",
                    {"x": {"dimension": ZERO}},
                    [],
                    [_rel(f"x**{2 * n + 1}", ">=", "0")],
                ),
            )
        )

    for a in range(0, 4):
        for b in range(0, 4):
            split = "dev" if a + b <= 2 else "val" if a + b <= 4 else "test"
            items.append(
                _item(
                    "two_shifted_squares",
                    f"twoshift-{a}-{b}",
                    split,
                    "true",
                    "ACCEPTED",
                    "smt_relative",
                    "Sum of two shifted squares is nonnegative.",
                    _payload(
                        f"(x-{a})**2 + (y-{b})**2 >= 0",
                        {"x": {"dimension": ZERO}, "y": {"dimension": ZERO}},
                        [],
                        [_rel(f"(x-({a}))**2 + (y-({b}))**2", ">=", "0")],
                    ),
                )
            )

    for a in range(1, 6):
        for b in range(a, 6):
            split = "dev" if b <= 3 else "val" if b == 4 else "test"
            items.append(
                _item(
                    "linear_sum_identity",
                    f"sum-id-{a}-{b}",
                    split,
                    "true",
                    "ACCEPTED",
                    "smt_relative",
                    "(x+a)+(x+b) = 2x+a+b.",
                    _payload(
                        f"(x+{a})+(x+{b}) == 2*x + {a + b}",
                        {"x": {"dimension": ZERO}},
                        [],
                        [_rel(f"(x+{a})+(x+{b})", "==", f"2*x + {a + b}")],
                    ),
                )
            )
            items.append(
                _item(
                    "linear_sum_false",
                    f"sum-false-{a}-{b}",
                    split,
                    "false",
                    "REFUTED",
                    "exact_rational_witness",
                    "Off-by-one on the constant term.",
                    _payload(
                        f"(x+{a})+(x+{b}) == 2*x + {a + b + 1}",
                        {"x": {"dimension": ZERO}},
                        [],
                        [_rel(f"(x+{a})+(x+{b})", "==", f"2*x + {a + b + 1}")],
                    ),
                )
            )

    seen, unique = set(), []
    for item in items:
        key = json.dumps(item["submission"], sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(key.encode()).hexdigest()
        item["canonical_sha256"] = digest
        if digest in seen:
            continue
        seen.add(digest)
        unique.append(item)
    return unique


def dump(directory: Path):
    directory.mkdir(parents=True, exist_ok=True)
    instances = build_instances()
    path = directory / "instances.jsonl"
    payload = "\n".join(json.dumps(item, ensure_ascii=False) for item in instances) + "\n"
    path.write_text(payload, encoding="utf-8")
    families = Counter(item["family"] for item in instances)
    splits = Counter(item["split"] for item in instances)
    manifest = {
        "id": VERSION,
        "license": "Same as this repository (synthetic original instances)",
        "provenance": "Hand-specified templates; parameters enumerate mathematically distinct constants, poles, degrees or SI pairs. Not an LLM-as-judge corpus.",
        "hidden_holdout": False,
        "holdout_note": "All splits are public in this repository and were inspected during development. This is a regression/evaluation set, not a secret test.",
        "count": len(instances),
        "families": dict(families),
        "splits": dict(splits),
        "instances_sha256": hashlib.sha256(payload.encode()).hexdigest(),
        "label_policy": "mathematical_status is assigned from the template. system_expected is the intended local pipeline behavior. Solver output is not the sole ground truth.",
        "calibration": None,
    }
    (directory / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (directory / "LICENSE.txt").write_text(
        "Synthetic original instances. Distributed under the repository license.\n",
        encoding="utf-8",
    )
    return manifest, instances


def load(directory: Path | None = None):
    directory = directory or Path(__file__).parent / "bench_data" / "v0.1"
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    instances = [
        json.loads(line)
        for line in (directory / "instances.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return manifest, instances


def evaluate(instances, runner=verify):
    rows = []
    for item in instances:
        result = runner(item["submission"])
        predicted = result["verdict"]
        expected = item["system_expected"]
        rows.append(
            {
                "id": item["id"],
                "family": item["family"],
                "split": item["split"],
                "mathematical_status": item["mathematical_status"],
                "system_expected": expected,
                "predicted": predicted,
                "match": predicted == expected,
                "duration_ms": result.get("duration_ms"),
                "reason": result.get("reason"),
                "operational_kind": result.get("operational_kind"),
                "evidence_types": sorted({o.get("trust") for o in result.get("obligations", [])}),
            }
        )
    return rows


def summarize(rows, manifest=None):
    n = len(rows)
    by_family = {}
    for row in rows:
        by_family.setdefault(row["family"], []).append(row)

    def rates(group):
        total = len(group)
        false_items = [r for r in group if r["mathematical_status"] in {"false", "ill_typed"}]
        true_items = [r for r in group if r["mathematical_status"] in {"true", "true_on_domain"}]
        accepts = [r for r in group if r["predicted"] == "ACCEPTED"]
        incorrect_accepts_on_false = [
            r for r in false_items if r["predicted"] == "ACCEPTED"
        ]
        incorrect_refutes_on_true = [r for r in true_items if r["predicted"] == "REFUTED"]
        abstentions = [r for r in group if r["predicted"] == "ABSTAIN"]
        timeouts = [r for r in group if r.get("operational_kind") == "timed_out"]
        operational = [r for r in group if r.get("operational_kind")]
        denom_false = len(false_items)
        denom_accepts = len(accepts)
        return {
            "n": total,
            "system_label_match": sum(r["match"] for r in group),
            "incorrect_accepts_on_false": len(incorrect_accepts_on_false),
            "denominator_false_or_illtyped": denom_false,
            "incorrect_accepts_among_accepts": (
                len([r for r in accepts if r["mathematical_status"] in {"false", "ill_typed"}])
                if denom_accepts
                else None
            ),
            "denominator_accepts": denom_accepts,
            "incorrect_refutes_on_true": len(incorrect_refutes_on_true),
            "denominator_true": len(true_items),
            "abstentions": len(abstentions),
            "timeouts": len(timeouts),
            "operational_failures": len(operational),
            "mean_latency_ms": round(sum(r["duration_ms"] or 0 for r in group) / total, 3) if total else None,
        }

    report = {
        "corpus": VERSION,
        "n": n,
        "overall": rates(rows),
        "by_family": {name: rates(group) for name, group in by_family.items()},
        "by_split": {
            split: rates([r for r in rows if r["split"] == split])
            for split in ("dev", "val", "test")
        },
        "calibration": None,
        "calibration_note": "No probabilistic scores are produced; ECE/Brier are not computed.",
        "zero_error_note": (
            "Zero observed incorrect accepts does not demonstrate zero risk. "
            "Report the false/ill-typed sample size (overall denominator_false_or_illtyped)."
        ),
        "scope": "Public evaluation set. Didactic UI cases are not evidence of generalization.",
        "manifest": manifest,
        "cases": rows,
    }
    return report

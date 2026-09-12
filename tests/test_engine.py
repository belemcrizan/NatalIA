import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from natalia.dsl import CompileError, dimension, parse
from natalia.engine import verify
from natalia.models import Submission, Variable

EXAMPLES = Path(__file__).parents[1] / "natalia" / "examples"


def submission(lhs="x**2", op=">=", rhs="0", assumptions=None):
    return {
        "title": "test",
        "variables": {"x": {"dimension": ["0"] * 7}},
        "assumptions": assumptions or [],
        "claims": [{"id": "claim", "kind": "relation", "lhs": lhs, "op": op, "rhs": rhs}],
        "budget_ms": 5000,
    }


@pytest.mark.parametrize("path", sorted(EXAMPLES.glob("*.json")), ids=lambda p: p.stem)
def test_acceptance_examples(path):
    case = json.loads(path.read_text(encoding="utf-8"))
    result = verify(case["submission"])
    assert result["verdict"] == case["expected_verdict"]
    assert result["confidence"] is None
    assert result["calibration"] == "not_available"
    assert result["input_sha256"]


@pytest.mark.parametrize(
    "expression",
    [
        "__import__('os')",
        "x.__class__",
        "x[0]",
        "[x for x in []]",
        "True",
        "1.5",
        "x**100",
        "x**x",
        "sum(x)",
        "sin(x, x)",
        "2**(8**8)",
        "x; print(x)",
    ],
)
def test_unsafe_or_unbounded_syntax_is_rejected(expression):
    assert verify(submission(expression))["verdict"] == "INVALID"


def test_undefined_variable_is_invalid():
    assert verify(submission("undeclared"))["verdict"] == "INVALID"


def test_fractional_dimensions_are_exact():
    variables = {"x": Variable(dimension=["0", "1", "0", "0", "0", "0", "0"])}
    node = parse("x**(1/2)*sqrt(x)", variables)
    assert dimension(node, variables) == tuple([0, 1, 0, 0, 0, 0, 0])


def test_dimension_error_short_circuits_solver():
    payload = submission("x+1")
    payload["variables"]["x"]["dimension"][0] = "1"
    result = verify(payload)
    assert result["verdict"] == "INVALID"
    assert not any(span["oracle"] == "z3" for span in result["spans"])


def test_transcendental_dimension_check():
    payload = submission("exp(x)")
    payload["variables"]["x"]["dimension"][1] = "1"
    assert verify(payload)["verdict"] == "INVALID"


def test_unsupported_functions_never_certify():
    assert verify(submission("exp(x)", ">", "0"))["verdict"] == "ABSTAIN"


def test_fractional_powers_never_certify():
    assert verify(submission("x**(1/2)", "==", "sqrt(x)"))["verdict"] == "ABSTAIN"


def test_counterexample_is_exact_and_domain_valid():
    result = verify(submission("x**2", ">=", "x", [{"lhs": "x", "op": ">", "rhs": "0"}]))
    assert result["verdict"] == "REFUTED"
    evidence = result["obligations"][-1]
    from fractions import Fraction

    x = Fraction(evidence["counterexample"]["x"])
    assert x > 0 and x * x < x
    assert evidence["trust"] == "exact_rational_witness"


def test_undefined_expression_in_assumption_abstains():
    assert (
        verify(submission(assumptions=[{"lhs": "x/x", "op": "==", "rhs": "1"}]))["verdict"]
        == "ABSTAIN"
    )


@pytest.mark.parametrize("lhs", ["x/x", "1/x", "x**(-1)", "0/x"])
def test_singular_expressions_never_accept_without_domain(lhs):
    assert verify(submission(lhs, "==", lhs))["verdict"] == "ABSTAIN"


def test_no_vacuous_acceptance():
    payload = submission(assumptions=[{"lhs": "x**2", "op": "<", "rhs": "0"}])
    result = verify(payload)
    assert result["verdict"] == "ABSTAIN"
    assert "Contradictory" in result["reason"]


def test_counterexample_dominates_open_hole():
    payload = submission("x", "==", "0")
    payload["claims"].append({"kind": "proof_hole", "id": "hole", "description": "Missing lemma"})
    assert verify(payload)["verdict"] == "REFUTED"


def test_algebraic_witness_abstains_without_rational_checker():
    payload = submission("x", "==", "0", [{"lhs": "x**2", "op": "==", "rhs": "2"}])
    assert verify(payload)["verdict"] == "ABSTAIN"


def test_hash_ignores_mapping_key_order():
    a = submission()
    assert verify(a)["input_sha256"] == verify(dict(reversed(list(a.items()))))["input_sha256"]


@pytest.mark.parametrize(
    "mutate",
    [
        lambda p: p.update(arbitrary=True),
        lambda p: p.update(claims=[]),
        lambda p: p.update(budget_ms=100000),
        lambda p: p["variables"]["x"].update(dimension=["0"] * 6),
        lambda p: p["variables"]["x"].update(dimension=["1/0"] * 7),
        lambda p: p["claims"].append(p["claims"][0]),
    ],
)
def test_wire_format_fails_closed(mutate):
    p = submission()
    mutate(p)
    with pytest.raises(ValidationError):
        Submission.model_validate(p)


def test_depth_bound():
    with pytest.raises(CompileError):
        parse("-" * 30 + "x", {"x": Variable()})


def test_ast_node_budget():
    with pytest.raises(CompileError):
        parse("+".join(["x"] * 50), {"x": Variable()})


@pytest.mark.parametrize("reserved", ["dimensions", "compile", "premises", "assumption-0"])
def test_reserved_obligation_ids(reserved):
    payload = submission()
    payload["claims"][0]["id"] = reserved
    with pytest.raises(ValidationError):
        Submission.model_validate(payload)


def test_zero_denominator_in_expected_limit_is_validation_error():
    payload = submission()
    payload["claims"] = [
        {"kind": "limit", "id": "asymptotic", "expression": "x", "variable": "x", "expected": "1/0"}
    ]
    with pytest.raises(ValidationError):
        Submission.model_validate(payload)

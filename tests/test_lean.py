from test_engine import submission

from natalia.engine import verify
from natalia.lean import check_export, classify_lean_output, export_square_nonneg


def test_comment_only_export_is_never_a_certificate():
    source = "-- only comments\n/- theorem natalia_obligation (x : ℝ) : True := rfl -/\n"
    result = check_export(source)
    assert result["checked"] is False
    assert result["classification"] == "export_not_a_proof"
    assert result["refutation"] is False
    assert result["trust"] != "kernel_certificate"


def test_sorry_export_is_incomplete_not_refuted():
    source = export_square_nonneg("abc", ["x"], {"lhs": "x**2", "op": ">=", "rhs": "0"})
    result = check_export(source)
    assert "sorry" in source
    assert result["checked"] is False
    assert result["classification"] == "incomplete_proof"
    assert result["refutation"] is False


def test_axiom_export_is_rejected():
    source = "theorem natalia_obligation (x : Nat) : True := True.intro\naxiom natalia_cheat : False\n"
    result = check_export(source)
    assert result["checked"] is False
    assert result["classification"] == "incomplete_proof"


def test_lean_failure_classes_are_not_refutations():
    assert classify_lean_output(
        returncode=1, stdout="", stderr="unknown identifier 'ℝ'", source="theorem natalia_obligation : True := rfl"
    ) == "dependency"
    assert classify_lean_output(
        returncode=1, stdout="", stderr="unexpected token ','", source="theorem natalia_obligation : True := rfl"
    ) == "syntax"
    assert classify_lean_output(
        returncode=1, stdout="", stderr="type mismatch", source="theorem natalia_obligation : True := rfl"
    ) == "type"
    assert (
        classify_lean_output(
            returncode=1, stdout="", stderr="", source="theorem natalia_obligation : True := rfl", timed_out=True
        )
        == "timeout"
    )


def test_certified_path_does_not_treat_lean_hole_as_refutation():
    payload = submission()
    payload["verification_mode"] = "certified"
    result = verify(payload)
    assert result["verdict"] == "ACCEPTED"
    assert result["guarantee_level"] == "KERNEL_CHECKED"
    kernel = next(item for item in result["obligations"] if item["adapter_id"] == "kernel")
    assert kernel["artifacts"]["lean_check"]["refutation"] is False
    assert kernel["artifacts"]["lean_check"]["checked"] is False

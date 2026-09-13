"""Live compilation preview. Does not dispatch solvers."""

from pydantic import ValidationError

from natalia.dsl import ZERO, CompileError, dimension, parse, relation_nodes
from natalia.models import Submission


def preview(payload: dict) -> dict:
    errors = []
    try:
        submission = Submission.model_validate(payload)
    except ValidationError as exc:
        for err in exc.errors():
            loc = ".".join(str(x) for x in err.get("loc", []))
            errors.append({"path": loc or "submission", "message": err.get("msg", "invalid")})
        return {"ok": False, "errors": errors, "obligations": [], "supported_fragment": False}

    obligations = []
    try:
        for assumption in submission.assumptions:
            relation_nodes(assumption, submission.variables)
        for claim in submission.claims:
            if claim.kind == "relation":
                relation_nodes(claim, submission.variables)
                obligations.append({"id": claim.id, "kind": "relation", "status": "compiled"})
            elif claim.kind == "limit":
                node = parse(claim.expression, submission.variables)
                if dimension(node, submission.variables) != ZERO:
                    raise CompileError("Local limit adapter requires a dimensionless expression")
                obligations.append({"id": claim.id, "kind": "limit", "status": "compiled"})
            else:
                obligations.append({"id": claim.id, "kind": "proof_hole", "status": "declared_gap"})
    except CompileError as exc:
        errors.append({"path": "expressions", "message": str(exc)})
        return {"ok": False, "errors": errors, "obligations": obligations, "supported_fragment": False}

    return {
        "ok": True,
        "errors": [],
        "obligations": obligations,
        "supported_fragment": True,
        "variables": list(submission.variables),
        "assumption_count": len(submission.assumptions),
        "note": "Compilation succeeded. This is not a proof and does not run solvers.",
    }

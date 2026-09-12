"""Deterministic compile/dispatch/aggregate baseline; no learned policy or calibration."""

import hashlib
import json
import platform
import uuid
from time import monotonic, time_ns

import sympy
import z3

from natalia import __version__
from natalia.dsl import ZERO, CompileError, Unsupported, dimension, parse, relation_nodes
from natalia.models import Submission
from natalia.oracles import SMTContext, limit_advisory


def base_result(payload):
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return {
        "verdict": "ABSTAIN",
        "confidence": None,
        "calibration": "not_available",
        "scope": "Explicit DSL over real numbers only; source_latex is not verified or translated.",
        "guarantee": "No Lean/kernel certificate. SMT-relative results and exact rational witnesses only.",
        "input_sha256": hashlib.sha256(canonical.encode()).hexdigest(),
        "policy": "deterministic-v1",
        "versions": {
            "natalia": __version__,
            "python": platform.python_version(),
            "z3": z3.get_version_string(),
            "sympy": sympy.__version__,
        },
        "obligations": [],
        "spans": [],
    }


def verify(payload):
    submission = Submission.model_validate(payload)
    result = base_result(submission.model_dump())
    start = monotonic()
    deadline = start + submission.budget_ms / 1000

    def record(name, oracle, action):
        tick, wall = monotonic(), time_ns()
        evidence = action()
        result["spans"].append(
            {
                "span_id": uuid.uuid4().hex[:16],
                "name": name,
                "oracle": oracle,
                "start_time_unix_ns": wall,
                "duration_ms": round((monotonic() - tick) * 1000, 3),
                "status": evidence.get("status", "ok"),
            }
        )
        return evidence

    def finish(verdict, reason):
        result.update(
            verdict=verdict, reason=reason, duration_ms=round((monotonic() - start) * 1000, 3)
        )
        result["proof_holes"] = [x["id"] for x in result["obligations"] if x["status"] == "unknown"]
        return result

    compiled = {}
    try:

        def compile_all():
            for index, assumption in enumerate(submission.assumptions):
                compiled[f"assumption-{index}"] = relation_nodes(assumption, submission.variables)
            for claim in submission.claims:
                if claim.kind == "relation":
                    compiled[claim.id] = relation_nodes(claim, submission.variables)
                elif claim.kind == "limit":
                    if claim.variable not in submission.variables:
                        raise CompileError("Limit variable must be declared")
                    node = parse(claim.expression, submission.variables)
                    if dimension(node, submission.variables) != ZERO:
                        raise CompileError(
                            "Local limit adapter requires a dimensionless expression"
                        )
                    compiled[claim.id] = node
            return {"status": "certified"}

        record("compile", "dimensions", compile_all)
    except CompileError as exc:
        result["obligations"].append(
            {"id": "compile", "oracle": "dimensions", "status": "invalid", "reason": str(exc)}
        )
        return finish("INVALID", "Static compilation failed before solver dispatch")

    result["obligations"].append(
        {
            "id": "dimensions",
            "oracle": "dimensions",
            "status": "certified",
            "reason": "SI dimensions checked with exact rational exponents",
        }
    )
    try:
        assumptions = [
            (a, *compiled[f"assumption-{i}"]) for i, a in enumerate(submission.assumptions)
        ]
        context = SMTContext(submission.variables, assumptions, deadline)
        domain = record("premise-consistency", "z3", lambda: {"status": str(context.check())})
        if domain["status"] != "sat":
            reason = (
                "Contradictory premises: vacuous acceptance is blocked"
                if domain["status"] == "unsat"
                else "Premise consistency could not be established"
            )
            result["obligations"].append(
                {"id": "premises", "oracle": "z3", "status": "unknown", "reason": reason}
            )
            return finish("ABSTAIN", reason)
    except (Unsupported, TimeoutError) as exc:
        result["obligations"].append(
            {"id": "premises", "oracle": "z3", "status": "unknown", "reason": str(exc)}
        )
        return finish("ABSTAIN", str(exc))

    for claim in submission.claims:
        oracle = {"relation": "z3", "limit": "sympy", "proof_hole": "unavailable"}[claim.kind]
        try:
            if monotonic() >= deadline:
                raise TimeoutError("Verification budget exhausted")
            if claim.kind == "relation":
                evidence = record(
                    claim.id, oracle, lambda: context.verify(claim, *compiled[claim.id])
                )
            elif claim.kind == "limit":
                if submission.assumptions:
                    raise Unsupported(
                        "Limit adapter does not certify compatibility of assumptions with infinity"
                    )
                evidence = record(
                    claim.id,
                    oracle,
                    lambda: limit_advisory(claim, compiled[claim.id], submission.variables),
                )
            else:
                evidence = {"status": "unknown", "reason": claim.description}
        except (Unsupported, TimeoutError, ZeroDivisionError) as exc:
            evidence = {"status": "unknown", "reason": str(exc)}
        result["obligations"].append({"id": claim.id, "oracle": oracle, **evidence})

    statuses = [o["status"] for o in result["obligations"]]
    if "refuted" in statuses:
        return finish(
            "REFUTED", "At least one claim has a validated counterexample under the stated premises"
        )
    if all(s == "certified" for s in statuses):
        return finish(
            "ACCEPTED", "All submitted obligations closed within the supported SMT fragment"
        )
    return finish(
        "ABSTAIN", "Some obligations remain open; no confidence estimate has been trained"
    )

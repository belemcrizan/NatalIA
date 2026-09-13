"""Independent polynomial identity / sum-of-squares checker for a small certified fragment.

This is not a general proof kernel and does not replace Lean. It reconstructs a
polynomial over Q from the same AST the DSL already accepted, then checks a
certificate bound to the obligation hash.
"""

from __future__ import annotations

import ast
from fractions import Fraction

from natalia.dsl import number
from natalia.evidence import obligation_hash
from natalia.evidence import record as evidence_record

FRAGMENT = "poly_sos_identity_q_v1"
ADAPTER_VERSION = "1.0"


def _vars(names):
    return tuple(sorted(names))


def _zero():
    return {}


def _add(a, b):
    out = dict(a)
    for key, coeff in b.items():
        out[key] = out.get(key, Fraction(0)) + coeff
        if out[key] == 0:
            out.pop(key)
    return out


def _scale(poly, factor):
    if factor == 0:
        return {}
    return {k: v * factor for k, v in poly.items()}


def _mul(a, b):
    out = {}
    for ka, ca in a.items():
        for kb, cb in b.items():
            key = tuple(x + y for x, y in zip(ka, kb))
            out[key] = out.get(key, Fraction(0)) + ca * cb
            if out[key] == 0:
                out.pop(key)
    return out


def _pow(poly, exponent: int):
    if exponent < 0:
        raise ValueError("Negative powers are outside the kernel fragment")
    if not poly:
        return {} if exponent else {(): Fraction(1)}
    width = len(next(iter(poly)))
    acc = {tuple(0 for _ in range(width)): Fraction(1)}
    for _ in range(exponent):
        acc = _mul(acc, poly)
    return acc


def ast_poly(node, names):
    width = len(names)
    index = {name: i for i, name in enumerate(names)}
    if isinstance(node, ast.Constant):
        return {tuple(0 for _ in range(width)): number(node)}
    if isinstance(node, ast.Name):
        exp = [0] * width
        exp[index[node.id]] = 1
        return {tuple(exp): Fraction(1)}
    if isinstance(node, ast.UnaryOp):
        inner = ast_poly(node.operand, names)
        return _scale(inner, -1 if isinstance(node.op, ast.USub) else 1)
    if isinstance(node, ast.Call):
        raise ValueError("Transcendental functions are outside the kernel fragment")
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        raise ValueError("Division is outside the kernel fragment")
    left, right = ast_poly(node.left, names), ast_poly(node.right, names)
    if isinstance(node.op, ast.Add):
        return _add(left, right)
    if isinstance(node.op, ast.Sub):
        return _add(left, _scale(right, -1))
    if isinstance(node.op, ast.Mult):
        return _mul(left, right)
    if isinstance(node.op, ast.Pow):
        power = number(node.right)
        if power.denominator != 1 or int(power) < 0:
            raise ValueError("Kernel fragment requires non-negative integer powers")
        return _pow(left, int(power))
    raise ValueError("Unsupported AST node in kernel fragment")


def _is_square_rational(value: Fraction) -> Fraction | None:
    if value < 0:
        return None

    def isqrt(n: int) -> int | None:
        if n < 0:
            return None
        root = int(n**0.5)
        while (root + 1) * (root + 1) <= n:
            root += 1
        while root * root > n:
            root -= 1
        return root if root * root == n else None

    num, den = isqrt(value.numerator), isqrt(value.denominator)
    if num is None or den is None:
        return None
    return Fraction(num, den)


def is_zero(poly):
    return not poly


def is_monomial_sos(poly):
    """Non-negative combination of squared monomials with square coefficients in Q."""
    terms = []
    for exponents, coeff in poly.items():
        if any(e % 2 for e in exponents):
            return None
        root = _is_square_rational(coeff)
        if root is None:
            return None
        half = tuple(e // 2 for e in exponents)
        terms.append({"coeff": str(root), "exponents": list(half)})
    return terms


def is_perfect_square(poly):
    """Return a polynomial square-root if `poly` is a square in Q[x]."""
    if is_zero(poly):
        return {}
    root = {}
    for _ in range(24):
        remaining = _add(poly, _scale(_mul(root, root), -1))
        if is_zero(remaining):
            return {",".join(str(e) for e in k): str(v) for k, v in root.items()}
        monomial = max(remaining, key=lambda e: (sum(e), e))
        coeff = remaining[monomial]
        if not root:
            if any(e % 2 for e in monomial):
                return None
            half_coeff = _is_square_rational(coeff)
            if half_coeff is None:
                return None
            term = {tuple(e // 2 for e in monomial): half_coeff}
        else:
            lead = max(root, key=lambda e: (sum(e), e))
            delta = tuple(a - b for a, b in zip(monomial, lead))
            if any(part < 0 for part in delta):
                return None
            denom = 2 * root[lead]
            if denom == 0:
                return None
            term = {delta: coeff / denom}
        root = _add(root, term)
        if len(root) > 16:
            return None
    return None


def obligation_payload(claim, assumptions, variables):
    return {
        "kind": claim.kind,
        "id": claim.id,
        "lhs": claim.lhs,
        "op": claim.op,
        "rhs": claim.rhs,
        "assumptions": [item.model_dump() for item in assumptions],
        "variables": {
            name: spec.model_dump(exclude_none=True) for name, spec in variables.items()
        },
        "fragment": FRAGMENT,
    }


def _difference(claim, names, compiled):
    lhs, rhs = compiled
    return _add(ast_poly(lhs, names), _scale(ast_poly(rhs, names), -1))


def try_certificate(claim, compiled, submission):
    if claim.kind != "relation":
        return None, "Kernel fragment supports relation claims only"
    if claim.op not in {"==", ">=", "<="}:
        return None, "Kernel fragment does not certify strict inequalities"
    names = _vars(submission.variables)
    try:
        diff = _difference(claim, names, compiled)
    except ValueError as exc:
        return None, str(exc)
    hashed = obligation_hash(obligation_payload(claim, submission.assumptions, submission.variables))
    if claim.op == "==":
        if not is_zero(diff):
            return None, "Polynomial difference is not identically zero"
        cert = {
            "kind": "identity",
            "fragment": FRAGMENT,
            "adapter_version": ADAPTER_VERSION,
            "obligation_hash": hashed,
            "variables": list(names),
            "proposition": {"lhs": claim.lhs, "op": claim.op, "rhs": claim.rhs, "id": claim.id},
        }
        return cert, "Polynomial identity on the nose"
    target = diff if claim.op == ">=" else _scale(diff, -1)
    square = is_perfect_square(target)
    if square is not None:
        cert = {
            "kind": "perfect_square",
            "fragment": FRAGMENT,
            "adapter_version": ADAPTER_VERSION,
            "obligation_hash": hashed,
            "variables": list(names),
            "square_root": square,
            "proposition": {"lhs": claim.lhs, "op": claim.op, "rhs": claim.rhs, "id": claim.id},
        }
        return cert, "Difference is a square in Q[x]"
    if submission.assumptions:
        return None, "Assumptions are outside the assumption-free SOS fragment"
    terms = is_monomial_sos(target)
    if terms is None:
        return None, "Not a documented sum of squared monomials"
    cert = {
        "kind": "monomial_sos",
        "fragment": FRAGMENT,
        "adapter_version": ADAPTER_VERSION,
        "obligation_hash": hashed,
        "variables": list(names),
        "terms": terms,
        "proposition": {"lhs": claim.lhs, "op": claim.op, "rhs": claim.rhs, "id": claim.id},
    }
    return cert, "Non-negative combination of squared monomials over Q"


def check_certificate(certificate, claim, compiled, submission):
    expected, reason = try_certificate(claim, compiled, submission)
    hashed = obligation_hash(obligation_payload(claim, submission.assumptions, submission.variables))
    if certificate.get("obligation_hash") != hashed:
        return False, "Certificate obligation_hash does not match this submission"
    if expected is None:
        return False, reason
    if certificate.get("kind") != expected.get("kind"):
        return False, "Certificate kind does not reconstruct"
    if certificate.get("fragment") != FRAGMENT:
        return False, "Unknown certificate fragment"
    if certificate.get("proposition") != expected.get("proposition"):
        return False, "Certificate proposition does not match the original claim"
    if expected["kind"] == "perfect_square" and certificate.get("square_root") != expected.get("square_root"):
        return False, "Square-root witness does not reconstruct"
    if expected["kind"] == "monomial_sos" and certificate.get("terms") != expected.get("terms"):
        return False, "SOS terms do not reconstruct"
    return True, reason


def evidence_for(claim, compiled, submission):
    cert, reason = try_certificate(claim, compiled, submission)
    if cert is None:
        return evidence_record(
            adapter_id="kernel",
            fragment=FRAGMENT,
            obligation_id=claim.id,
            payload=obligation_payload(claim, submission.assumptions, submission.variables),
            status="unknown",
            reason=reason,
            trust="unavailable",
            validation="not_run",
            adapter_version=ADAPTER_VERSION,
        )
    ok, checked = check_certificate(cert, claim, compiled, submission)
    return evidence_record(
        adapter_id="kernel",
        fragment=FRAGMENT,
        obligation_id=claim.id,
        payload=obligation_payload(claim, submission.assumptions, submission.variables),
        status="certified" if ok else "unknown",
        reason=checked,
        trust="kernel_certificate" if ok else "unavailable",
        validation="independent_pass" if ok else "independent_fail",
        adapter_version=ADAPTER_VERSION,
        extra={"artifacts": {"certificate": cert}},
    )

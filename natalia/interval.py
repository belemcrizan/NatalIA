"""Exact rational interval arithmetic for regional refutation on a declared box.

Operations use Fraction endpoints. Enclosures are sound for +, -, *, integer
powers and division when the divisor interval does not contain zero. This is not
a substitute for a kernel certificate, and it does not use binary floating point.
"""

from __future__ import annotations

import ast
from fractions import Fraction

from natalia.dsl import CompileError, number
from natalia.evidence import record as evidence_record


class Interval:
    __slots__ = ("lo", "hi")

    def __init__(self, lo: Fraction, hi: Fraction):
        if lo > hi:
            raise ValueError("Empty interval")
        self.lo, self.hi = lo, hi

    def __add__(self, other):
        return Interval(self.lo + other.lo, self.hi + other.hi)

    def __sub__(self, other):
        return Interval(self.lo - other.hi, self.hi - other.lo)

    def __mul__(self, other):
        candidates = (
            self.lo * other.lo,
            self.lo * other.hi,
            self.hi * other.lo,
            self.hi * other.hi,
        )
        return Interval(min(candidates), max(candidates))

    def reciprocal(self):
        if self.lo <= 0 <= self.hi:
            raise ZeroDivisionError("Interval contains zero")
        a, b = 1 / self.lo, 1 / self.hi
        return Interval(min(a, b), max(a, b))

    def __truediv__(self, other):
        return self * other.reciprocal()

    def pow_int(self, exponent: int):
        if exponent == 0:
            return Interval(Fraction(1), Fraction(1))
        if exponent < 0:
            return self.pow_int(-exponent).reciprocal()
        if exponent % 2 == 0:
            if self.lo >= 0:
                return Interval(self.lo**exponent, self.hi**exponent)
            if self.hi <= 0:
                return Interval(self.hi**exponent, self.lo**exponent)
            return Interval(Fraction(0), max(self.lo**exponent, self.hi**exponent))
        return Interval(self.lo**exponent, self.hi**exponent)

    def strictly_less(self, other):
        return self.hi < other.lo

    def strictly_greater(self, other):
        return self.lo > other.hi


def eval_interval(node, boxes):
    if isinstance(node, ast.Constant):
        value = number(node)
        return Interval(value, value)
    if isinstance(node, ast.Name):
        return boxes[node.id]
    if isinstance(node, ast.UnaryOp):
        inner = eval_interval(node.operand, boxes)
        if isinstance(node.op, ast.USub):
            return Interval(-inner.hi, -inner.lo)
        return inner
    if isinstance(node, ast.Call):
        raise CompileError("Interval adapter does not enclose transcendental calls")
    left, right = eval_interval(node.left, boxes), eval_interval(node.right, boxes)
    if isinstance(node.op, ast.Add):
        return left + right
    if isinstance(node.op, ast.Sub):
        return left - right
    if isinstance(node.op, ast.Mult):
        return left * right
    if isinstance(node.op, ast.Div):
        return left / right
    power = number(node.right)
    if power.denominator != 1:
        raise CompileError("Interval adapter requires integer powers")
    return left.pow_int(int(power))


def boxes_from_variables(variables):
    boxes = {}
    for name, spec in variables.items():
        if spec.domain_min is None or spec.domain_max is None:
            return None
        boxes[name] = Interval(Fraction(spec.domain_min), Fraction(spec.domain_max))
    return boxes


def compare_intervals(op, left: Interval, right: Interval):
    if op == ">=":
        if left.strictly_less(right):
            return "false"
        if left.lo >= right.hi:
            return "true"
    elif op == ">":
        if left.hi <= right.lo:
            return "false"
        if left.strictly_greater(right):
            return "true"
    elif op == "<=":
        if left.strictly_greater(right):
            return "false"
        if left.hi <= right.lo:
            return "true"
    elif op == "<":
        if left.lo >= right.hi:
            return "false"
        if left.strictly_less(right):
            return "true"
    elif op == "==":
        if left.strictly_less(right) or left.strictly_greater(right):
            return "false"
        if left.lo == left.hi == right.lo == right.hi:
            return "true"
    elif op == "!=":
        if left.strictly_less(right) or left.strictly_greater(right):
            return "true"
        if left.lo == left.hi == right.lo == right.hi:
            return "false"
    return "unknown"


def refute_on_box(claim, lhs, rhs, variables):
    boxes = boxes_from_variables(variables)
    if boxes is None:
        return evidence_record(
            adapter_id="interval",
            fragment="exact_rational_box",
            obligation_id=f"interval-{claim.id}",
            payload={"kind": "interval", "id": claim.id},
            status="unknown",
            reason="Interval adapter requires finite domain_min and domain_max on every variable",
            trust="unavailable",
            validation="not_run",
        )
    try:
        left = eval_interval(lhs, boxes)
        right = eval_interval(rhs, boxes)
        outcome = compare_intervals(claim.op, left, right)
    except (ZeroDivisionError, CompileError, ValueError) as exc:
        return evidence_record(
            adapter_id="interval",
            fragment="exact_rational_box",
            obligation_id=f"interval-{claim.id}",
            payload={"kind": "interval", "id": claim.id},
            status="unknown",
            reason=str(exc),
            trust="unavailable",
            validation="not_run",
        )
    artifact = {
        "region": {name: [str(box.lo), str(box.hi)] for name, box in boxes.items()},
        "lhs_enclosure": [str(left.lo), str(left.hi)],
        "rhs_enclosure": [str(right.lo), str(right.hi)],
        "rounding": "exact_rational_endpoints",
        "illustration": False,
    }
    if outcome == "false":
        return evidence_record(
            adapter_id="interval",
            fragment="exact_rational_box",
            obligation_id=f"interval-{claim.id}",
            payload={"kind": "interval", "id": claim.id, "region": artifact["region"]},
            status="refuted",
            reason="Enclosure shows the relation fails throughout the declared box",
            trust="interval_enclosure",
            validation="independent_pass",
            extra={"artifacts": artifact},
        )
    if outcome == "true":
        return evidence_record(
            adapter_id="interval",
            fragment="exact_rational_box",
            obligation_id=f"interval-{claim.id}",
            payload={"kind": "interval", "id": claim.id, "region": artifact["region"]},
            status="unknown",
            reason="Enclosure is consistent with the claim on the box; it is not a global certificate",
            trust="interval_enclosure",
            extra={"artifacts": artifact},
        )
    return evidence_record(
        adapter_id="interval",
        fragment="exact_rational_box",
        obligation_id=f"interval-{claim.id}",
        payload={"kind": "interval", "id": claim.id, "region": artifact["region"]},
        status="unknown",
        reason="Interval image intersects both sides of the relation; result is inconclusive",
        trust="interval_enclosure",
        extra={"artifacts": artifact},
    )

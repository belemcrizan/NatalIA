"""Bounded adapters. SMT validity is relative to an explicit real-arithmetic encoding."""

import ast
import operator
from fractions import Fraction
from time import monotonic

import sympy as sp
import z3

from natalia.dsl import Unsupported, number

OPS = {
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
}


def smt_expr(node, symbols, guards):
    if isinstance(node, ast.Constant):
        return z3.RealVal(str(number(node)))
    if isinstance(node, ast.Name):
        return symbols[node.id]
    if isinstance(node, ast.UnaryOp):
        a = smt_expr(node.operand, symbols, guards)
        return -a if isinstance(node.op, ast.USub) else a
    if isinstance(node, ast.Call):
        raise Unsupported("Transcendental functions and sqrt are outside the SMT adapter")
    a = smt_expr(node.left, symbols, guards)
    if isinstance(node.op, ast.Pow):
        power = number(node.right)
        if power.denominator != 1:
            raise Unsupported("Fractional powers require a future domain-aware adapter")
        n = int(power)
        if n < 0:
            guards.append(a != 0)
        return a**n if n >= 0 else 1 / a ** (-n)
    b = smt_expr(node.right, symbols, guards)
    if isinstance(node.op, ast.Add):
        return a + b
    if isinstance(node.op, ast.Sub):
        return a - b
    if isinstance(node.op, ast.Mult):
        return a * b
    guards.append(b != 0)
    return a / b


def exact_expr(node, values):
    if isinstance(node, ast.Constant):
        return number(node)
    if isinstance(node, ast.Name):
        return values[node.id]
    if isinstance(node, ast.UnaryOp):
        a = exact_expr(node.operand, values)
        return -a if isinstance(node.op, ast.USub) else a
    a, b = exact_expr(node.left, values), exact_expr(node.right, values)
    if isinstance(node.op, ast.Add):
        return a + b
    if isinstance(node.op, ast.Sub):
        return a - b
    if isinstance(node.op, ast.Mult):
        return a * b
    if isinstance(node.op, ast.Div):
        return a / b
    return a ** int(b)


class SMTContext:
    def __init__(self, variables, assumptions, deadline):
        self.symbols = {name: z3.Real(name) for name in variables}
        self.assumptions = assumptions
        self.deadline = deadline
        self.solver = z3.SolverFor("QF_NRA")
        self.solver.set(random_seed=0)
        for name, spec in variables.items():
            lo, hi = spec.domain_min, spec.domain_max
            if lo is not None:
                self.solver.add(self.symbols[name] >= z3.RealVal(str(lo)))
            if hi is not None:
                self.solver.add(self.symbols[name] <= z3.RealVal(str(hi)))
        for relation, lhs, rhs in assumptions:
            guards = []
            formula = OPS[relation.op](
                smt_expr(lhs, self.symbols, guards), smt_expr(rhs, self.symbols, guards)
            )
            # Assumptions may restrict a domain; undefined expressions are never silently totalized.
            if any(not z3.is_true(z3.simplify(g)) for g in guards):
                raise Unsupported(
                    "Assumptions must not contain potentially undefined divisions/powers"
                )
            self.solver.add(formula)

    def check(self):
        remaining = int((self.deadline - monotonic()) * 1000)
        if remaining <= 0:
            raise TimeoutError("Verification budget exhausted")
        self.solver.set(timeout=max(1, min(remaining, 2000)))
        return self.solver.check()

    def verify(self, relation, lhs, rhs):
        guards = []
        formula = OPS[relation.op](
            smt_expr(lhs, self.symbols, guards), smt_expr(rhs, self.symbols, guards)
        )
        if guards:
            self.solver.push()
            self.solver.add(z3.Not(z3.And(*guards)))
            defined = self.check()
            self.solver.pop()
            if defined != z3.unsat:
                return {
                    "status": "unknown",
                    "reason": "Domain safety not established; add nonzero assumptions",
                }
        self.solver.push()
        try:
            self.solver.add(z3.Not(formula))
            smtlib = self.solver.to_smt2()
            outcome = self.check()
            if outcome == z3.unsat:
                return {
                    "status": "certified",
                    "reason": "Negation is UNSAT under consistent premises",
                    "trust": "smt_relative",
                    "smtlib": smtlib,
                }
            if outcome == z3.unknown:
                return {
                    "status": "unknown",
                    "reason": self.solver.reason_unknown(),
                    "smtlib": smtlib,
                }
            model = self.solver.model()
            values = {}
            for name, symbol in self.symbols.items():
                value = model.eval(symbol, model_completion=True)
                if not z3.is_rational_value(value):
                    return {
                        "status": "unknown",
                        "reason": "Algebraic witness requires independent validation",
                        "smtlib": smtlib,
                    }
                values[name] = Fraction(value.numerator_as_long(), value.denominator_as_long())
            premises_hold = all(
                OPS[r.op](exact_expr(a, values), exact_expr(b, values))
                for r, a, b in self.assumptions
            )
            left, right = exact_expr(lhs, values), exact_expr(rhs, values)
            if not premises_hold or OPS[relation.op](left, right):
                return {
                    "status": "unknown",
                    "reason": "Independent rational witness check failed",
                    "validation": "independent_fail",
                }
            return {
                "status": "refuted",
                "reason": "Counterexample independently checked with exact rational arithmetic",
                "trust": "exact_rational_witness",
                "validation": "independent_pass",
                "counterexample": {k: str(v) for k, v in values.items()},
                "evaluation": {"lhs": str(left), "op": relation.op, "rhs": str(right)},
                "smtlib": smtlib,
            }
        finally:
            self.solver.pop()


def cas_expr(node, symbols):
    if isinstance(node, ast.Constant):
        return sp.Integer(node.value)
    if isinstance(node, ast.Name):
        return symbols[node.id]
    if isinstance(node, ast.UnaryOp):
        a = cas_expr(node.operand, symbols)
        return -a if isinstance(node.op, ast.USub) else a
    if isinstance(node, ast.Call):
        if node.func.id != "exp":
            raise Unsupported("Local asymptotic adapter supports rational expressions and exp only")
        return sp.exp(cas_expr(node.args[0], symbols))
    a = cas_expr(node.left, symbols)
    if isinstance(node.op, ast.Pow):
        p = number(node.right)
        if p.denominator != 1:
            raise Unsupported("Fractional asymptotic powers deferred")
        return a ** int(p)
    b = cas_expr(node.right, symbols)
    if isinstance(node.op, ast.Add):
        return a + b
    if isinstance(node.op, ast.Sub):
        return a - b
    if isinstance(node.op, ast.Mult):
        return a * b
    return a / b


def limit_advisory(claim, node, variables):
    symbols = {name: sp.Symbol(name, real=True) for name in variables}
    expression = cas_expr(node, symbols)
    if expression.free_symbols - {symbols[claim.variable]}:
        raise Unsupported("Asymptotic adapter requires a single free variable")
    expected = Fraction(claim.expected)
    result = sp.limit(expression, symbols[claim.variable], sp.oo)
    return {
        "status": "unknown",
        "reason": "CAS result is advisory; no kernel certificate is available",
        "cas_result": str(result),
        "expected": str(expected),
        "matches_expected": bool(result == sp.Rational(expected.numerator, expected.denominator)),
        "trust": "cas_advisory",
    }

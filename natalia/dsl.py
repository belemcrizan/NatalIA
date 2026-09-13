"""Parse a deliberately small expression language, never eval/sympify strings."""

import ast
from fractions import Fraction

ZERO = (Fraction(0),) * 7
FUNCTIONS = {"exp", "log", "sin", "cos", "sqrt"}
SI_LABELS = ("massa", "comprimento", "tempo", "corrente", "temperatura", "quantidade", "intensidade")
NAMED_DIMENSIONS = {
    (1, 0, 0, 0, 0, 0, 0): "massa",
    (0, 1, 0, 0, 0, 0, 0): "comprimento",
    (0, 0, 1, 0, 0, 0, 0): "tempo",
    (1, 1, -1, 0, 0, 0, 0): "momento",
    (1, 2, -2, 0, 0, 0, 0): "energia",
    (0, 1, -1, 0, 0, 0, 0): "velocidade",
    (0, 0, 0, 0, 0, 0, 0): "grandeza adimensional",
}


def describe_dimension(values):
    key = tuple(int(v) if v.denominator == 1 else v for v in values)
    if key in NAMED_DIMENSIONS:
        return NAMED_DIMENSIONS[key]
    parts = [f"{label}^{exp}" for label, exp in zip(SI_LABELS, values) if exp != 0]
    return " · ".join(parts) if parts else "grandeza adimensional"


class CompileError(ValueError):
    pass


class Unsupported(ValueError):
    pass


def number(node):
    if isinstance(node, ast.Constant) and type(node.value) is int and abs(node.value) <= 10**9:
        return Fraction(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        return number(node.operand) * (-1 if isinstance(node.op, ast.USub) else 1)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        try:
            return number(node.left) / number(node.right)
        except ZeroDivisionError as exc:
            raise CompileError("Zero denominator") from exc
    raise CompileError("Use small integers or rational literals (e.g. 1/2), not floats")


def parse(source, variables):
    try:
        root = ast.parse(source, mode="eval").body
    except (SyntaxError, RecursionError) as exc:
        raise CompileError("Invalid expression syntax; use explicit * and **") from exc
    if sum(1 for _ in ast.walk(root)) > 100:
        raise CompileError("Expression exceeds 100 AST nodes")

    def check(node, depth=0):
        if depth > 20:
            raise CompileError("Expression exceeds depth 20")
        if isinstance(node, ast.Name):
            if node.id not in variables:
                raise CompileError(f"Undeclared variable: {node.id}")
        elif isinstance(node, ast.Constant):
            number(node)
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
            check(node.operand, depth + 1)
        elif isinstance(node, ast.BinOp) and isinstance(
            node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)
        ):
            check(node.left, depth + 1)
            check(node.right, depth + 1)
            if isinstance(node.op, ast.Pow) and abs(number(node.right)) > 8:
                raise CompileError("Power exponent must be rational with absolute value <= 8")
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in FUNCTIONS
            and len(node.args) == 1
            and not node.keywords
        ):
            check(node.args[0], depth + 1)
        else:
            raise CompileError(
                "Unsupported syntax; attributes, indexing and arbitrary calls are forbidden"
            )

    check(root)
    return root


def dimension(node, variables):
    if isinstance(node, ast.Constant):
        return ZERO
    if isinstance(node, ast.Name):
        return tuple(Fraction(x) for x in variables[node.id].dimension)
    if isinstance(node, ast.UnaryOp):
        return dimension(node.operand, variables)
    if isinstance(node, ast.Call):
        arg = dimension(node.args[0], variables)
        if node.func.id == "sqrt":
            return tuple(x / 2 for x in arg)
        if arg != ZERO:
            raise CompileError(f"{node.func.id} requires a dimensionless argument")
        return ZERO
    left, right = dimension(node.left, variables), dimension(node.right, variables)
    if isinstance(node.op, (ast.Add, ast.Sub)):
        if left != right:
            raise CompileError(
                f"Esta soma mistura {describe_dimension(left)} e {describe_dimension(right)}. "
                "Revise as dimensões ou os fatores da expressão."
            )
        return left
    if isinstance(node.op, ast.Mult):
        return tuple(a + b for a, b in zip(left, right))
    if isinstance(node.op, ast.Div):
        return tuple(a - b for a, b in zip(left, right))
    exponent = number(node.right)
    return tuple(x * exponent for x in left)


def relation_nodes(relation, variables):
    lhs, rhs = parse(relation.lhs, variables), parse(relation.rhs, variables)
    ld, rd = dimension(lhs, variables), dimension(rhs, variables)

    # Literal zero is polymorphic only at a relation boundary, never an implicit unit.
    def is_zero(node):
        try:
            return number(node) == 0
        except CompileError:
            return False

    if ld != rd and not is_zero(lhs) and not is_zero(rhs):
        raise CompileError(
            f"Esta relação compara {describe_dimension(ld)} com {describe_dimension(rd)}. "
            "Revise as dimensões ou os fatores da expressão."
        )
    return lhs, rhs

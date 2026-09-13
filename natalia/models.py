"""Versioned, bounded wire format. Unknown fields fail closed."""

import re
from fractions import Fraction
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Expression = Annotated[str, Field(min_length=1, max_length=512)]
Rational = Annotated[str, Field(pattern=r"^-?\d{1,6}(/\d{1,6})?$", max_length=14)]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Variable(StrictModel):
    dimension: list[Rational] = Field(default_factory=lambda: ["0"] * 7, min_length=7, max_length=7)
    domain_min: Rational | None = None
    domain_max: Rational | None = None

    @field_validator("dimension")
    @classmethod
    def rational_dimensions(cls, values):
        for value in values:
            try:
                if abs(Fraction(value)) > 100:
                    raise ValueError("Dimension exponent exceeds 100")
            except ZeroDivisionError as exc:
                raise ValueError("Dimension denominator cannot be zero") from exc
        return values

    @model_validator(mode="after")
    def ordered_domain(self):
        if self.domain_min is not None and self.domain_max is not None:
            if Fraction(self.domain_min) > Fraction(self.domain_max):
                raise ValueError("domain_min must be <= domain_max")
        return self


class Relation(StrictModel):
    lhs: Expression
    op: Literal["==", "!=", ">", ">=", "<", "<="] = "=="
    rhs: Expression


class RelationClaim(Relation):
    kind: Literal["relation"] = "relation"
    id: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_-]{0,39}$")


class LimitClaim(StrictModel):
    kind: Literal["limit"]
    id: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_-]{0,39}$")
    expression: Expression
    variable: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_]{0,23}$")
    target: Literal["infinity"] = "infinity"
    expected: Rational

    @field_validator("expected")
    @classmethod
    def valid_expected(cls, value):
        try:
            Fraction(value)
        except ZeroDivisionError as exc:
            raise ValueError("Expected limit denominator cannot be zero") from exc
        return value


class HoleClaim(StrictModel):
    kind: Literal["proof_hole"]
    id: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_-]{0,39}$")
    description: str = Field(min_length=1, max_length=1000)


Claim = Annotated[RelationClaim | LimitClaim | HoleClaim, Field(discriminator="kind")]


class Submission(StrictModel):
    schema_version: Literal["1.0"] = "1.0"
    title: str = Field(min_length=1, max_length=160)
    source_latex: str = Field(default="", max_length=8000)
    variables: dict[str, Variable] = Field(min_length=1, max_length=20)
    assumptions: list[Relation] = Field(default_factory=list, max_length=20)
    claims: list[Claim] = Field(min_length=1, max_length=20)
    budget_ms: int = Field(default=5000, ge=250, le=15000, strict=True)
    verification_mode: Literal["fast", "certified", "lean"] = "fast"
    critical: bool = False

    @field_validator("variables")
    @classmethod
    def safe_names(cls, values):
        for name in values:
            if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,23}", name) or name in {
                "exp",
                "log",
                "sin",
                "cos",
                "sqrt",
                "True",
                "False",
                "None",
            }:
                raise ValueError(f"Invalid/reserved variable name: {name}")
        return values

    @model_validator(mode="after")
    def unique_claims(self):
        ids = [c.id for c in self.claims]
        if any(
            i in {"dimensions", "compile", "premises"} or i.startswith("assumption-") for i in ids
        ):
            raise ValueError("Claim IDs collide with reserved compiler IDs")
        if len(ids) != len(set(ids)):
            raise ValueError("Claim IDs must be unique")
        return self

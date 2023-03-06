from dataclasses import dataclass, field
from typing import Any, Optional

from sylva.location import Location
from sylva.builtins import (
    ComplexType,
    FloatType,
    IntType,
    SylvaObject,
    SylvaType,
)
from sylva.operator import Operator


@dataclass(kw_only=True)
class Expr(SylvaObject):
    location: Location = field(default_factory=Location.Generate)
    type: Optional[SylvaType]


@dataclass(kw_only=True)
class LookupExpr(Expr):
    name: str


@dataclass(kw_only=True)
class LiteralExpr(Expr):
    value: Any


@dataclass(kw_only=True)
class UnaryExpr(Expr):
    operator: Operator
    expr: Expr


@dataclass(kw_only=True)
class BinaryExpr(Expr):
    operator: Operator
    lhs: Expr
    rhs: Expr


@dataclass(kw_only=True)
class AttributeLookupExpr(Expr):
    name: str
    obj: Expr
    reflection: bool = False


@dataclass(kw_only=True)
class ReflectionLookupExpr(Expr):
    name: str
    obj: Expr


@dataclass(kw_only=True)
class CallExpr(Expr):
    function: Expr
    arguments: list[Expr]
    monomorphization_index: int = 0


@dataclass(kw_only=True)
class IntExpr(Expr):
    type: IntType


@dataclass(kw_only=True)
class FloatExpr(Expr):
    type: FloatType


@dataclass(kw_only=True)
class ComplexExpr(Expr):
    type: ComplexType

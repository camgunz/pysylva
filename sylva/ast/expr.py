from dataclasses import dataclass
from typing import Any, Optional

from sylva.ast.node import Node
from sylva.ast.operator import Operator
from sylva.ast.sylva_type import SylvaType


@dataclass(kw_only=True)
class Expr(Node):
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

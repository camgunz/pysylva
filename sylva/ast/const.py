from dataclasses import dataclass
from typing import Any

from sylva.ast.expr import Expr


@dataclass(kw_only=True)
class ConstExpr(Expr):
    pass


@dataclass(kw_only=True)
class ConstLookupExpr(ConstExpr):
    name: str


@dataclass(kw_only=True)
class ConstLiteralExpr(ConstExpr):
    value: Any


@dataclass(kw_only=True)
class ConstAttributeLookupExpr(ConstExpr):
    name: str
    obj: ConstExpr
    reflection: bool = False


@dataclass(kw_only=True)
class ConstReflectionLookupExpr(ConstExpr):
    name: str
    obj: ConstExpr

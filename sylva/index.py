from dataclasses import dataclass

from sylva.expr import Expr
from sylva.number import IntExpr


@dataclass(kw_only=True)
class IndexExpr(Expr):
    indexable: Expr
    index: IntExpr

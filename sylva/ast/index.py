from dataclasses import dataclass

from sylva.ast.expr import Expr
from sylva.ast.number import IntExpr


@dataclass(kw_only=True)
class IndexExpr(Expr):
    indexable: Expr
    index: IntExpr

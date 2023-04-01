from dataclasses import dataclass

from sylva import errors
from sylva.builtins import SylvaObject
from sylva.expr import CallExpr, LookupExpr
from sylva.mod import Mod
from sylva.visitor import Visitor


@dataclass(kw_only=True)
class LookupExprTypeAssigner(Visitor):

    def enter_lookup_expr(
        self,
        lookup_expr: LookupExpr,
        name: str,
        parents: list[SylvaObject | Mod]
    ):
        val_type = self.lookup(lookup_expr.name)
        if val_type is None:
            raise errors.UndefinedSymbol(
                lookup_expr.location, lookup_expr.name
            )
        lookup_expr.type = val_type

    def enter_call_expr(
        self, call_expr: CallExpr, name: str, parents: list[SylvaObject | Mod]
    ):
        pass

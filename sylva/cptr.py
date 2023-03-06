from dataclasses import dataclass

from .expr import Expr


@dataclass(kw_only=True)
class CPtrExpr(Expr):
    expr: Expr
    is_exclusive: bool
    referenced_type_is_exclusive: bool

    def __init__(
        self, location, expr, is_exclusive, referenced_type_is_exclusive
    ):
        from .type_singleton import TypeSingletons

        Expr.__init__(
            self,
            location=location,
            type=TypeSingletons.CPTR.get_or_create_monomorphization(
                location,
                expr.type,
                is_exclusive,
                referenced_type_is_exclusive=referenced_type_is_exclusive
            )[1]
        )
        self.expr = expr
        self.is_exclusive = is_exclusive
        self.referenced_type_is_exclusive = referenced_type_is_exclusive

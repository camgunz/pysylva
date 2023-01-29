from dataclasses import dataclass, field
from functools import cached_property

from .expr import Expr
from .sylva_type import MonoType


@dataclass(kw_only=True)
class CVoidType(MonoType):
    name: str = field(init=False, default='cvoid')

    @cached_property
    def mname(self):
        return 'cvoid'


@dataclass(kw_only=True)
class CVoidExpr(Expr):
    expr: Expr

    def __init__(self, location, expr):
        from .type_singleton import TypeSingletons

        Expr.__init__(self, location=location, type=TypeSingletons.CVOID)
        self.expr = expr

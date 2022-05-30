from functools import cached_property

from .expr import BaseExpr
from .sylva_type import SylvaType


class CVoidType(SylvaType):

    @cached_property
    def mname(self):
        return '5cvoid'


class CVoidExpr(BaseExpr):

    def __init__(self, location, expr):
        from .type_singleton import TypeSingletons

        BaseExpr.__init__(self, location, TypeSingletons.CVOID)
        self.expr = expr

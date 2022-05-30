from functools import cached_property

from .expr import BaseExpr
from .sylva_type import SylvaType


class CVoidType(SylvaType):

    def __init__(self, location):
        from .type_singleton import get_int_type

        SylvaType.__init__(self, location)
        self.llvm_type = get_int_type(bits=8, signed=True).llvm_type

    @cached_property
    def mname(self):
        return 'cvoid'


class CVoidExpr(BaseExpr):

    def __init__(self, location, expr):
        from .type_singleton import TypeSingletons

        BaseExpr.__init__(self, location, TypeSingletons.CVOID)
        print(expr)
        self.expr = expr

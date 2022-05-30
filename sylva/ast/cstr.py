from functools import cached_property

from llvmlite import ir

from .literal import LiteralExpr
from .sylva_type import SylvaType


class CStrType(SylvaType):

    def __init__(self, location):
        SylvaType.__init__(self, location)
        self.llvm_type = ir.PointerType(ir.IntType(8))

    @cached_property
    def mname(self):
        return 'cstr'


class CStrLiteralExpr(LiteralExpr):

    def __init__(self, location, value):
        from .type_singleton import TypeSingletons

        LiteralExpr.__init__(self, location, TypeSingletons.CSTR, value)

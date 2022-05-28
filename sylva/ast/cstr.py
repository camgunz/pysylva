from functools import cached_property

from llvmlite import ir

from .literal import LiteralExpr
from .sylva_type import SylvaType
from .type_singleton import TypeSingletons
from .value import ValueExpr


class CStrType(SylvaType):

    def __init__(self, location):
        SylvaType.__init__(self, location)
        self.llvm_type = ir.PointerType(ir.IntType(8))

    @cached_property
    def mname(self):
        return '4cstr'


class CStrLiteralExpr(LiteralExpr):

    def __init__(self, location, value):
        LiteralExpr.__init__(self, location, TypeSingletons.CSTR.value, value)


class CStrExpr(ValueExpr):

    def __init__(self, location):
        ValueExpr.__init__(self, location, TypeSingletons.CSTR.value)

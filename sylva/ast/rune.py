from functools import cached_property

from llvmlite import ir

from .literal import LiteralExpr
from .type_singleton import TypeSingletons
from .sylva_type import SylvaType
from .value import ValueExpr


class RuneType(SylvaType):

    def __init__(self, location):
        SylvaType.__init__(self, location)
        self.llvm_type = ir.IntType(32)

    @cached_property
    def mname(self):
        return '1r'


class RuneLiteralExpr(LiteralExpr):

    def __init__(self, location, value):
        LiteralExpr.__init__(self, location, TypeSingletons.RUNE.value, value)


class RuneExpr(ValueExpr):

    def __init__(self, location):
        ValueExpr.__init__(self, location, TypeSingletons.RUNE.value)

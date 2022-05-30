from functools import cached_property

from llvmlite import ir

from .literal import LiteralExpr
from .sylva_type import SylvaType


class RuneType(SylvaType):

    def __init__(self, location):
        SylvaType.__init__(self, location)
        self.llvm_type = ir.IntType(32)

    @cached_property
    def mname(self):
        return 'rune'


class RuneLiteralExpr(LiteralExpr):

    def __init__(self, location, value):
        from .type_singleton import TypeSingletons

        LiteralExpr.__init__(self, location, TypeSingletons.RUNE, value)

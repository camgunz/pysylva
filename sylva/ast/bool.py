from functools import cached_property

from llvmlite import ir

from .literal import LiteralExpr
from .type_singleton import TypeSingletons
from .sylva_type import SylvaType
from .value import ValueExpr


class BoolType(SylvaType):

    def __init__(self, location):
        SylvaType.__init__(self, location)
        self.llvm_type = ir.IntType(8)

    @cached_property
    def mname(self):
        return '1b'


class BoolLiteralExpr(LiteralExpr):

    def __init__(self, location, value):
        LiteralExpr.__init__(
            self,
            location=location,
            type=TypeSingletons.BOOL.value,
            value=value
        )

    def emit(self, module, builder, scope):
        return self.type.llvm_type(1 if self.value else 0)


class BoolExpr(ValueExpr):

    def __init__(self, location):
        ValueExpr.__init__(
            self, location=location, type=TypeSingletons.BOOL.value
        )

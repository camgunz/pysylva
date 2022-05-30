from functools import cached_property

from llvmlite import ir

from .literal import LiteralExpr
from .sylva_type import SylvaType


class BoolType(SylvaType):

    def __init__(self, location):
        SylvaType.__init__(self, location)
        self.llvm_type = ir.IntType(8)

    @cached_property
    def mname(self):
        return 'bool'


class BoolLiteralExpr(LiteralExpr):

    def __init__(self, location, value):
        from .type_singleton import TypeSingletons

        LiteralExpr.__init__(
            self, location=location, type=TypeSingletons.BOOL, value=value
        )

    def emit(self, obj, module, builder, scope, name):
        return self.type.llvm_type(1 if self.value else 0)

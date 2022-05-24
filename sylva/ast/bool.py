from functools import cached_property

from llvmlite import ir

from attrs import define, field

from .expr import LiteralExpr, ValueExpr
from .type_singleton import TypeSingletons
from .sylva_type import SylvaType


@define(eq=False, slots=True)
class BoolType(SylvaType):

    def get_value_expr(self, location):
        return BoolExpr(location=location, type=self)

    @llvm_type.default # noqa: F821
    def _llvm_type_factory(self):
        return ir.IntType(8)

    @cached_property
    def mname(self):
        return '1b'


@define(eq=False, slots=True)
class BoolLiteralExpr(LiteralExpr):
    type = field(init=False, default=TypeSingletons.BOOL.value)

    @classmethod
    def FromRawValue(cls, location, raw_value):
        return cls(location, value=raw_value == 'true')

    def emit(self, module, builder, scope):
        return self.type.llvm_type(1 if self.value else 0)


@define(eq=False, slots=True)
class BoolExpr(ValueExpr):
    type = field(init=False, default=TypeSingletons.BOOL.value)

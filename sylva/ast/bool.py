from functools import cached_property

from llvmlite import ir # type: ignore

from attrs import define, field

from .expr import LiteralExpr, ValueExpr
from .type_singleton import TypeSingletons
from .sylva_type import SylvaType


@define(eq=False, slots=True)
class BoolType(SylvaType):
    llvm_type = field(init=False)

    def get_value_expr(self, location):
        return BoolExpr(location=location, type=self)

    # pylint: disable=no-self-use
    @llvm_type.default
    def _llvm_type_factory(self):
        return ir.IntType(8)

    @cached_property
    def mname(self):
        return '1b'


@define(eq=False, slots=True)
class BoolLiteralExpr(LiteralExpr):
    type: BoolType = TypeSingletons.BOOL.value

    @classmethod
    def FromRawValue(cls, location, raw_value):
        return cls(location, value=raw_value == 'true')

    # pylint: disable=unused-argument
    def emit(self, module, builder, scope):
        return self.type.llvm_type(1 if self.value else 0)


@define(eq=False, slots=True)
class BoolExpr(ValueExpr):
    type: BoolType = TypeSingletons.BOOL.value

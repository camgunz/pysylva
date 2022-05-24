from functools import cached_property

from llvmlite import ir # type: ignore

from attrs import define, field

from .expr import LiteralExpr, ValueExpr
from .type_singleton import TypeSingletons
from .sylva_type import SylvaType


@define(eq=False, slots=True)
class RuneType(SylvaType):
    llvm_type = field(init=False)

    def get_value_expr(self, location):
        return RuneExpr(location=location, type=self)

    # pylint: disable=no-self-use,unused-argument
    @llvm_type.default
    def _llvm_type_factory(self):
        return ir.IntType(32)

    # pylint: disable=no-self-use
    @cached_property
    def mname(self):
        return '1r'


@define(eq=False, slots=True)
class RuneLiteralExpr(LiteralExpr):
    type: RuneType = TypeSingletons.RUNE.value

    @classmethod
    def FromRawValue(cls, location, raw_value):
        return cls(location, value=raw_value[1:-1])


@define(eq=False, slots=True)
class RuneExpr(ValueExpr):
    type: RuneType = TypeSingletons.RUNE.value

from functools import cached_property

from llvmlite import ir

from attrs import define, field

from .expr import LiteralExpr, ValueExpr
from .type_singleton import TypeSingletons
from .sylva_type import SylvaType


@define(eq=False, slots=True)
class RuneType(SylvaType):

    def get_value_expr(self, location):
        return RuneExpr(location=location, type=self)

    @llvm_type.default # noqa: F821
    def _llvm_type_factory(self):
        return ir.IntType(32)

    @cached_property
    def mname(self):
        return '1r'


@define(eq=False, slots=True)
class RuneLiteralExpr(LiteralExpr):
    type = field(init=False, default=TypeSingletons.RUNE.value)

    @classmethod
    def FromRawValue(cls, location, raw_value):
        return cls(location, value=raw_value[1:-1])


@define(eq=False, slots=True)
class RuneExpr(ValueExpr):
    type = field(init=False, default=TypeSingletons.RUNE.value)

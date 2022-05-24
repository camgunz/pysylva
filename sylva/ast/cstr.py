from functools import cached_property

from attrs import define, field
from llvmlite import ir

from .expr import LiteralExpr, ValueExpr
from .type_singleton import TypeSingletons
from .sylva_type import SylvaType


@define(eq=False, slots=True)
class CStrType(SylvaType):

    @llvm_type.default # noqa: F821
    def _llvm_type_factory(self):
        return ir.PointerType(ir.IntType(8))

    @cached_property
    def mname(self):
        return '4cstr'


@define(eq=False, slots=True)
class CStrLiteralExpr(LiteralExpr):
    type = field(init=False, default=TypeSingletons.CSTR.value)

    @classmethod
    def FromRawValue(cls, location, raw_value):
        return cls(location, value=raw_value[1:-1])


@define(eq=False, slots=True)
class CStrExpr(ValueExpr):
    type = field(init=False, default=TypeSingletons.CSTR.value)

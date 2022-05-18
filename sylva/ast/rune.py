from llvmlite import ir # type: ignore

from attrs import define

from .expr import LiteralExpr, ValueExpr
from .type_singleton import TypeSingleton
from .sylva_type import LLVMTypeMixIn, SylvaType
from ..location import Location


@define(eq=False, slots=True)
class RuneType(SylvaType, LLVMTypeMixIn):

    # pylint: disable=no-self-use
    def mangle(self):
        return '1r'

    def get_value_expr(self, location):
        return RuneExpr(location=location, type=self)

    # pylint: disable=no-self-use,unused-argument
    def get_llvm_type(self, module):
        return ir.IntType(32)


@define(eq=False, slots=True)
class RuneLiteralExpr(LiteralExpr):
    type: RuneType = RuneType(Location.Generate())

    @classmethod
    def FromRawValue(cls, location, raw_value):
        return cls(location, value=raw_value[1:-1])


@define(eq=False, slots=True)
class RuneExpr(ValueExpr):
    type: RuneType = TypeSingleton.RUNE.value

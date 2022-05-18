from llvmlite import ir # type: ignore

from attrs import define, field

from .expr import LiteralExpr, ValueExpr
from .type_singleton import TypeSingletons
from .sylva_type import SylvaType
from ..location import Location


@define(eq=False, slots=True)
class RuneType(SylvaType):
    llvm_type = field(init=False)

    # pylint: disable=no-self-use
    def mangle(self):
        return '1r'

    def get_value_expr(self, location):
        return RuneExpr(location=location, type=self)

    # pylint: disable=no-self-use,unused-argument
    @llvm_type.default
    def _llvm_type_factory(self):
        return ir.IntType(32)


@define(eq=False, slots=True)
class RuneLiteralExpr(LiteralExpr):
    type: RuneType = RuneType(Location.Generate())

    @classmethod
    def FromRawValue(cls, location, raw_value):
        return cls(location, value=raw_value[1:-1])


@define(eq=False, slots=True)
class RuneExpr(ValueExpr):
    type: RuneType = TypeSingletons.RUNE.value

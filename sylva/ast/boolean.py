from llvmlite import ir # type: ignore

from attrs import define

from .expr import LiteralExpr, ValueExpr
from .type_singleton import TypeSingletons
from .sylva_type import LLVMTypeMixIn, SylvaType
from ..location import Location


@define(eq=False, slots=True)
class BooleanType(SylvaType, LLVMTypeMixIn):

    # pylint: disable=no-self-use
    def mangle(self):
        return '1b'

    def get_value_expr(self, location):
        return BooleanExpr(location=location, type=self)

    # pylint: disable=no-self-use,unused-argument
    def get_llvm_type(self, module):
        return ir.IntType(8)


@define(eq=False, slots=True)
class BooleanLiteralExpr(LiteralExpr):
    type: BooleanType = BooleanType(Location.Generate())

    @classmethod
    def FromRawValue(cls, location, raw_value):
        return cls(location, value=raw_value == 'true')

    # pylint: disable=unused-argument
    def emit_llvm_expr(self, module, builder):
        return self.type.get_llvm_type(module)(1 if self.value else 0)


@define(eq=False, slots=True)
class BooleanExpr(ValueExpr):
    type: BooleanType = TypeSingletons.BOOL.value

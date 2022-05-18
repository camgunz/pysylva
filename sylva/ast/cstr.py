from attrs import define
from llvmlite import ir # type: ignore

from .expr import LiteralExpr, ValueExpr
from .type_singleton import TypeSingletons
from .sylva_type import LLVMTypeMixIn, SylvaType


@define(eq=False, slots=True)
class CStrType(SylvaType, LLVMTypeMixIn):

    # pylint: disable=unused-argument
    def get_llvm_type(self, module):
        return ir.PointerType(ir.IntType(8))


@define(eq=False, slots=True)
class CStrLiteralExpr(LiteralExpr):
    type: CStrType = TypeSingletons.CSTR.value

    @classmethod
    def FromRawValue(cls, location, raw_value):
        return cls(location, value=raw_value[1:-1])


@define(eq=False, slots=True)
class CStrExpr(ValueExpr):
    type: CStrType = TypeSingletons.CSTR.value

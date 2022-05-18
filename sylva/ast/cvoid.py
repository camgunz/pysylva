from attrs import define

from .expr import Expr
from .number import IntegerType
from .type_singleton import TypeSingletons
from .sylva_type import LLVMTypeMixIn, SylvaType


@define(eq=False, slots=True)
class CVoidType(SylvaType, LLVMTypeMixIn):

    # pylint: disable=unused-argument
    def get_llvm_type(self, module):
        raise RuntimeError('Cannot get the LLVM type of CVoid')


@define(eq=False, slots=True)
class CVoidExpr(Expr):
    expr: Expr
    type: IntegerType = TypeSingletons.CVOID.value

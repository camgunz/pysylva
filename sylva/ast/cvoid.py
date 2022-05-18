from attrs import define

from .expr import Expr
from .number import IntType
from .type_singleton import TypeSingletons
from .sylva_type import SylvaType


@define(eq=False, slots=True)
class CVoidType(SylvaType):

    # pylint: disable=unused-argument
    @llvm_type.default
    def _llvm_type_factory(self):
        raise RuntimeError('Cannot get the LLVM type of CVoid')


@define(eq=False, slots=True)
class CVoidExpr(Expr):
    expr: Expr
    type: IntType = TypeSingletons.CVOID.value

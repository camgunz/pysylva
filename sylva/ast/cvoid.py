from functools import cached_property

from attrs import define, field

from .expr import Expr
from .number import IntType
from .type_singleton import TypeSingletons
from .sylva_type import SylvaType


@define(eq=False, slots=True)
class CVoidType(SylvaType):
    llvm_type = field(init=False)

    # pylint: disable=unused-argument,no-self-use
    @llvm_type.default
    def _llvm_type_factory(self):
        raise RuntimeError('Cannot get the LLVM type of CVoid')

    @cached_property
    def mname(self):
        return '5cvoid'


@define(eq=False, slots=True)
class CVoidExpr(Expr):
    expr: Expr
    type: IntType = TypeSingletons.CVOID.value

from attrs import define

from .base import Node
from .operator import Operator
from .reflection_lookup import ReflectionLookupMixIn
from .sylva_type import SylvaType


@define(eq=False, slots=True)
class Expr(Node, ReflectionLookupMixIn):
    type: SylvaType

    # pylint: disable=no-self-use
    def get_reflection_attribute_type(self, location, name):
        from .array import ArrayType
        if name == 'type':
            return SylvaType
        if name == 'bytes':
            return ArrayType

    def reflect_attribute(self, location, name):
        if name == 'type':
            return self.type
        if name == 'bytes':
            pass

    def emit(self, module, builder, scope):
        raise NotImplementedError()


@define(eq=False, slots=True)
class ValueExpr(Expr):
    pass


@define(eq=False, slots=True)
class LiteralExpr(Expr):
    type: SylvaType
    value: bool | float | int | str

    # pylint: disable=unused-argument
    def emit(self, module, builder, scope):
        return self.type.llvm_type(self.value)


@define(eq=False, slots=True)
class IndexExpr(Expr):
    indexable: Expr
    index: Expr


@define(eq=False, slots=True)
class BinaryExpr(Expr):
    operator: Operator
    lhs: Expr
    rhs: Expr

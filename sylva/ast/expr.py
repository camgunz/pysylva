from attrs import define, field

from .base import Node
from .reflection_lookup import ReflectionLookupMixIn
from .sylva_type import SylvaType


@define(eq=False, slots=True)
class Expr(Node, ReflectionLookupMixIn):
    type = field()

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
    value = field()

    def emit(self, module, builder, scope):
        return self.type.llvm_type(self.value)


@define(eq=False, slots=True)
class IndexExpr(Expr):
    indexable = field()
    index = field()


@define(eq=False, slots=True)
class BinaryExpr(Expr):
    operator = field()
    lhs = field()
    rhs = field()

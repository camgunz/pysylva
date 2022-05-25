from attrs import define, field

from .. import errors
from .attribute_lookup import AttributeLookupMixIn
from .base import Node
from .reflection_lookup import ReflectionLookupMixIn


@define(eq=False, slots=True)
class Expr(Node, AttributeLookupMixIn, ReflectionLookupMixIn):
    type = field()

    def get_attribute(self, location, name):
        for impl in self.type.implementations:
            for func in impl.funcs:
                if func.name == name:
                    return func.type
        raise errors.NoSuchAttribute(location, name)

    def emit_attribute_lookup(self, location, module, builder, scope, name):
        for impl in self.type.implementations:
            for func in impl.funcs:
                if func.name == name:
                    return ValueExpr(
                        location=location, type=func.type, value=func
                    )
        raise errors.NoSuchAttribute(location, name)

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

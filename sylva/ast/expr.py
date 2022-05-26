from attrs import define, field

from .. import errors
from .attribute_lookup import AttributeLookupMixIn
from .base import Node
from .reflection_lookup import ReflectionLookupMixIn


@define(eq=False, slots=True)
class BaseExpr(Node):
    type = field()

    def emit(self, module, builder, scope):
        raise NotImplementedError()


@define(eq=False, slots=True)
class ValueExpr(BaseExpr, AttributeLookupMixIn, ReflectionLookupMixIn):

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


@define(eq=False, slots=True)
class LiteralExpr(ValueExpr):
    value = field()

    def emit(self, module, builder, scope):
        return self.type.llvm_type(self.value)


@define(eq=False, slots=True)
class IndexExpr(BaseExpr):
    indexable = field()
    index = field()


@define(eq=False, slots=True)
class BinaryExpr(BaseExpr):
    operator = field()
    lhs = field()
    rhs = field()

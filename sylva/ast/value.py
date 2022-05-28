# from .. import errors
from .attribute_lookup import AttributeLookupMixIn
from .base import Node
from .expr import BaseExpr
from .reflection_lookup import ReflectionLookupMixIn


class Value(Node):

    def __init__(self, location, name, ptr, type):
        Node.__init__(self, location)
        self.name = name
        self.ptr = ptr
        self.type = type

    def emit(self, module, builder, scope):
        return builder.load(self.ptr, self.name)


class ValueExpr(BaseExpr, AttributeLookupMixIn, ReflectionLookupMixIn):

    def __init__(self, location, type):
        BaseExpr.__init__(self, location=location, type=type)
        AttributeLookupMixIn.__init__(self, location=location)
        ReflectionLookupMixIn.__init__(self, location=location)

    # def get_attribute(self, location, name):
    #     for impl in self.type.implementations:
    #         for func in impl.funcs:
    #             if func.name == name:
    #                 return func.type
    #     raise errors.NoSuchAttribute(location, name)

    # def emit_attribute_lookup(self, location, module, builder, scope, name):
    #     for impl in self.type.implementations:
    #         for func in impl.funcs:
    #             if func.name == name:
    #                 return ValueExpr(
    #                     location=location, type=func.type, value=func
    #                 )
    #     raise errors.NoSuchAttribute(location, name)

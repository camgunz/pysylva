from .. import errors
from .expr import BaseExpr


class ReflectionLookupMixIn:

    def __init__(self, location):
        self.location = location
        self.reflection_attributes = {}

    def get_reflection_attribute(self, name):
        return self.reflection_attributes.get(name)

    def set_reflection_attribute(self, attribute):
        existing_attribute = self.get_reflection_attribute(attribute.name)
        if existing_attribute:
            raise errors.DuplicateDefinition(
                attribute.name,
                attribute.location,
                existing_attribute.location
            )
        self.reflection_attributes[attribute.name] = attribute

    def emit_reflection_lookup(self, module, builder, scope, name):
        ra = self.get_reflection_attribute(name)
        if ra is None:
            raise errors.NoSuchAttribute(self.location, name)
        return ra.emit(self, self.location, module, builder, scope)


class ReflectionLookupExpr(BaseExpr):

    def __init__(self, location, expr, name):
        super().__init__(location, expr.get_reflection_attribute(name).type)
        self.expr = expr
        self.name = name

    def emit(self, module, builder, scope):
        return self.expr.emit_reflection_lookup(
            self.location, module, builder, scope, self.name
        )

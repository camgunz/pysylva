from .. import errors
from .expr import BaseExpr


class AttributeLookupMixIn:

    def __init__(self, location):
        self.location = location
        self.attributes = {}

    def get_attribute(self, name):
        return self.attributes.get(name)

    def set_attribute(self, attribute):
        existing_attribute = self.get_attribute(attribute.name)
        if existing_attribute:
            raise errors.DuplicateDefinition(
                attribute.name,
                attribute.location,
                existing_attribute.location
            )
        self.attributes[attribute.name] = attribute

    def emit_attribute_lookup(self, module, builder, scope, name):
        a = self.get_attribute(name)
        if a is None:
            raise errors.NoSuchAttribute(self.location, name)
        return a.emit(self, self.location, module, builder, scope)


class AttributeLookupExpr(BaseExpr):

    def __init__(self, location, expr, name):
        super().__init__(location, expr.type.get_attribute(name).type)
        self.expr = expr
        self.name = name

    def emit(self, module, builder, scope):
        return self.expr.emit_attribute_lookup(
            self.location, module, builder, scope, self.name
        )

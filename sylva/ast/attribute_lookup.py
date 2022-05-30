from .. import errors
from .expr import BaseExpr


class AttributeLookupMixIn:

    def __init__(self):
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
            return None
        a.emit(self, module, builder, scope, name)


class AttributeLookupExpr(BaseExpr):

    def __init__(self, location, type, name, obj):
        super().__init__(location, type)
        self.name = name
        self.obj = obj

    def emit(self, obj, module, builder, scope, name):
        result = self.obj.emit_attribute_lookup(
            module, builder, scope, self.name
        )

        if result is None:
            raise errors.NoSuchAttribute(self.location, self.name)

        return result

from .. import errors
from .expr import BaseExpr


class ReflectionLookupMixIn:

    def __init__(self):
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
            return None
        return ra.emit(self, module, builder, scope, name)


class ReflectionLookupExpr(BaseExpr):

    def __init__(self, location, type, name, obj):
        super().__init__(location, type)
        self.name = name
        self.obj = obj

    def emit(self, obj, module, builder, scope, name):
        result = self.obj.emit_reflection_lookup(
            module, builder, scope, self.name
        )

        if result is None:
            raise errors.NoSuchAttribute(self.location, self.name)

        return result

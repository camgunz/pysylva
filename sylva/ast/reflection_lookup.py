from attrs import define, field

from .. import errors
from .expr import BaseExpr


@define(eq=False, slots=True)
class ReflectionLookupMixIn:
    reflection_attributes = field(init=False, default={})

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


@define(eq=False, slots=True)
class ReflectionLookupExpr(BaseExpr):
    type = field(init=False)
    expr = field()
    name = field()

    @type.default
    def _type_factory(self):
        return self.expr.get_reflection_attribute_type(
            self.location, self.name
        )

    def emit(self, module, builder, scope):
        return self.expr.emit_reflection_lookup(
            self.location, module, builder, scope, self.name
        )

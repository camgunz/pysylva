from attrs import define, field

from .. import errors
from .expr import BaseExpr


@define(eq=False, slots=True)
class AttributeLookupMixIn:
    attributes = field(init=False, default={})

    def get_attribute(self, location, name):
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


@define(eq=False, slots=True)
class AttributeLookupExpr(BaseExpr):
    type = field(init=False)
    expr = field()
    name = field()

    @type.default
    def _type_factory(self):
        return self.expr.get_attribute(self.location, self.name).type

    def emit(self, module, builder, scope):
        return self.expr.emit_attribute_lookup(
            self.location, module, builder, scope, self.name
        )

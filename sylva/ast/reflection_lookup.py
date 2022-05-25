from attrs import define, field

from .. import errors
from .expr import Expr
from .type_mapping import Attribute


@define(eq=False, slots=True)
class ReflectionAttribute(Attribute):
    func = field()
    index = field(init=False, default=None)

    def __call__(self, obj, location):
        return self.func(obj, location)


@define(eq=False, slots=True)
class ReflectionLookupMixIn:
    reflection_attributes = field(init=False, default=[])

    def get_reflection_attribute(self, name):
        for ra in self.reflection_attributes:
            if ra.name == name:
                return ra

    def set_reflection_attribute(self, attribute):
        existing_attribute = self.get_reflection_attribute(attribute.name)
        if existing_attribute:
            raise errors.DuplicateDefinition(
                attribute.name,
                attribute.location,
                existing_attribute.location
            )
        self.reflection_attributes.append(attribute)

    def emit_reflection_lookup(self, location, module, builder, scope, name):
        ra = self.get_reflection_attribute(name)
        if ra is None:
            raise errors.NoSuchAttribute(location, name)
        return ra(self, location)


@define(eq=False, slots=True)
class ReflectionLookupExpr(Expr):
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

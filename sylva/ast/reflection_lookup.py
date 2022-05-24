from attrs import define, field

from .expr import Expr


@define(eq=False, slots=True)
class ReflectionLookupMixIn:

    def get_reflection_attribute_type(self, location, name):
        raise NotImplementedError()

    def reflect_attribute(self, location, name):
        raise NotImplementedError()


@define(eq=False, slots=True)
class ReflectionLookupExpr(Expr):
    type = field(init=False)
    expr: Expr | ReflectionLookupMixIn
    name: str

    @type.default
    def _type_factory(self):
        return self.expr.get_reflection_attribute_type(
            self.location, self.name
        )

    # pylint: disable=unused-argument
    def emit(self, module, builder, scope):
        return self.expr.reflect_attribute(self.location, self.name)

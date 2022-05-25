from attrs import define, field

from .expr import Expr


@define(eq=False, slots=True)
class AttributeLookupMixIn:

    def get_attribute(self, location, name):
        raise NotImplementedError()

    def emit_attribute_lookup(self, location, module, builder, scope, name):
        raise NotImplementedError()


@define(eq=False, slots=True)
class AttributeLookupExpr(Expr):
    expr = field()
    name = field()

    @type.default
    def _type_factory(self):
        return self.expr.get_attribute(self.location, self.name).type

    def emit(self, module, builder, scope):
        return self.expr.emit_attribute_lookup(
            self.location, module, builder, scope, self.name
        )

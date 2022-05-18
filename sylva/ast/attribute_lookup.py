from attrs import define, field

from .expr import Expr


@define(eq=False, slots=True)
class AttributeLookupMixIn:

    def get_attribute(self, location, name):
        raise NotImplementedError()

    def emit_attribute_lookup(self, location, name):
        raise NotImplementedError()


@define(eq=False, slots=True)
class AttributeLookupExpr(Expr):
    type = field(init=False)
    expr: Expr | AttributeLookupMixIn
    attribute: str | int

    @type.default
    def _type_factory(self):
        return self.expr.get_attribute(self.location, self.attribute).type

    # pylint: disable=unused-argument
    def emit(self, module, builder):
        return self.expr.lookup_attribute(self.location, self.attribute)

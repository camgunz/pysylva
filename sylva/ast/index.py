from attrs import define, field

from .expr import Expr


@define(eq=False, slots=True)
class IndexMixIn:

    def get_index_type(self, location, index):
        raise NotImplementedError()

    def get_index(self, location, index):
        raise NotImplementedError()


@define(eq=False, slots=True)
class IndexExpr(Expr):
    type = field(init=False)
    expr: Expr | IndexMixIn
    index: int

    @type.default
    def _type_factory(self):
        return self.expr.get_index_type(self.location, self.name)

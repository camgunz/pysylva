from attrs import define, field

from .. import errors
from .expr import BaseExpr


@define(eq=False, slots=True)
class LookupExpr(BaseExpr):
    name = field()

    def emit(self, module, builder, scope):
        value = scope.get(self.name)
        if value is None:
            raise errors.UndefinedSymbol(self.location, self.name)
        return value

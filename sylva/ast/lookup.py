from .. import errors
from .expr import BaseExpr


class LookupExpr(BaseExpr):

    def __init__(self, location, type, name):
        BaseExpr.__init__(self, location, type)
        self.name = name

    def emit(self, module, builder, scope):
        value = scope.get(self.name)
        if value is None:
            raise errors.UndefinedSymbol(self.location, self.name)
        return value

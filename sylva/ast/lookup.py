from .. import errors
from .expr import BaseExpr


class LookupExpr(BaseExpr):

    def __init__(self, location, type, name):
        BaseExpr.__init__(self, location, type)
        self.name = name

    def emit(self, *args, **kwargs):
        module = kwargs['module']
        scope = kwargs['scope']

        value = scope.get(self.name)

        if value is None:
            value = module.emit_attribute_lookup(name=self.name)

        if value is None:
            raise errors.UndefinedSymbol(self.location, self.name)

        return value

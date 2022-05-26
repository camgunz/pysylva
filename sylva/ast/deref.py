from attrs import define, field

from .. import errors
from .expr import BaseExpr


@define(eq=False, slots=True)
class DerefExpr(BaseExpr):
    ptr = field()
    name_expr = field()

    def emit(self, module, builder, scope):
        name = name_expr.emit(module, builder, scope)
        return builder.load(self.ptr, name)

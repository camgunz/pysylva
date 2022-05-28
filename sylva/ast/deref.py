from .expr import BaseExpr


class DerefExpr(BaseExpr):

    def __init__(self, location, type, ptr, name_expr):
        BaseExpr.__init__(super, location, type)
        self.ptr = ptr
        self.name_expr = name_expr

    def emit(self, module, builder, scope):
        name = self.name_expr.emit(module, builder, scope)
        return builder.load(self.ptr, name)

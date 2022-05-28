from .expr import BaseExpr


class LiteralExpr(BaseExpr):

    def __init__(self, location, type, value):
        BaseExpr.__init__(self, location=location, type=type)
        self.value = value

    def emit(self, module, builder, scope):
        return self.type.llvm_type(self.value)

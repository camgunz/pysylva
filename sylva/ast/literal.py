from .value import ValueExpr


class LiteralExpr(ValueExpr):

    def __init__(self, location, type, value):
        ValueExpr.__init__(self, location, type)
        self.value = value

    def emit(self, module, builder, scope):
        return self.type.llvm_type(self.value)

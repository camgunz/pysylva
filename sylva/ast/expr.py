from .base import Node


class BaseExpr(Node):

    def __init__(self, location, type):
        Node.__init__(self, location)
        self.type = type

    def emit(self, obj, module, builder, scope, name):
        raise NotImplementedError()


class IndexExpr(BaseExpr):

    def __init__(self, location, type, indexable, index):
        super().__init__(location, type)
        self.indexable = indexable
        self.index = index


class BinaryExpr(BaseExpr):

    def __init__(self, location, type, operator, lhs, rhs):
        super().__init__(location, type)
        self.operator = operator
        self.lhs = lhs
        self.rhs = rhs

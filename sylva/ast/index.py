from .expr import BaseExpr


class IndexMixIn:

    def get_index_type(self, location, index):
        raise NotImplementedError()

    def get_index(self, location, index):
        raise NotImplementedError()


class IndexExpr(BaseExpr):

    def __init__(self, location, type, expr, index):
        BaseExpr.__init__(self, location, expr.get_index_type(location, index))
        self.expr = expr
        self.index = index

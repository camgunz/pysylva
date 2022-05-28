from .. import errors
from .bool import BoolType
from .expr import BaseExpr
from .number import IntType, NumericType


class UnaryExpr(BaseExpr):

    def __init__(self, location, type, operator, expr):
        if operator == '+' and not isinstance(expr.type, NumericType):
            raise errors.InvalidExpressionType(self.location, 'number')
        if operator == '-' and not isinstance(expr.type, NumericType):
            raise errors.InvalidExpressionType(self.location, 'number')
        if operator == '~' and not isinstance(expr.type, IntType):
            raise errors.InvalidExpressionType(self.location, 'integer')
        if operator == '!' and not isinstance(expr.type, BoolType):
            raise errors.InvalidExpressionType(self.location, 'bool')
        BaseExpr.__init__(self, location, expr.type)
        self.operator = operator
        self.expr = expr

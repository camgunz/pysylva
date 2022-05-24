from attrs import define, field

from .. import errors
from .bool import BoolType
from .expr import Expr
from .number import IntType, NumericType


@define(eq=False, slots=True)
class UnaryExpr(Expr):
    operator: str = field()
    expr: Expr

    # pylint: disable=unused-argument
    @operator.validator
    def check_value(self, attribute, op):
        if op == '+' and not isinstance(self.expr.type, NumericType):
            raise errors.InvalidExpressionType(self.location, 'number')
        if op == '-' and not isinstance(self.expr.type, NumericType):
            raise errors.InvalidExpressionType(self.location, 'number')
        if op == '~' and not isinstance(self.expr.type, IntType):
            raise errors.InvalidExpressionType(self.location, 'integer')
        if op == '!' and not isinstance(self.expr.type, BoolType):
            raise errors.InvalidExpressionType(self.location, 'bool')

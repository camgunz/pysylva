from abc import ABC, abstractmethod
import decimal

from . import errors


class ASTNode(ABC):

    def __init__(self, location):
        self.location = location

    @abstractmethod
    def _parse(self, value):
        ...

    @abstractmethod
    def emit(self, codegen):
        ...


class Expr(ASTNode):

    # pylint: disable=no-self-use
    def _parse(self, value):
        return value


class LiteralExpr(Expr):

    def __init__(self, location, value):
        super().__init__(location)
        self.raw_value = value
        self.value = self._parse(value)

    def __repr__(self):
        return '%s(%r)' % (
            self.__class__.__name__,
            self.value
        )


class BooleanExpr(LiteralExpr):

    def _parse(self, value):
        if value == 'true':
            return True
        if value == 'false':
            return False
        raise errors.LiteralParseFailure(self)

    def emit(self, codegen):
        codegen.emit_boolean(self.value)


class RuneExpr(LiteralExpr):

    def emit(self, codegen):
        codegen.emit_rune(self.value)


class StringExpr(LiteralExpr):

    def emit(self, codegen):
        codegen.emit_string(self.value)


class DecimalExpr(LiteralExpr):  # [TODO] Rounding modes

    def _parse(self, value):
        try:
            return decimal.Decimal(value)
        except Exception:
            raise errors.LiteralParseFailure(self)

    def emit(self, codegen):
        codegen.emit_decimal(self.value)


class FloatExpr(LiteralExpr):  # [TODO] Rounding modes

    def _parse(self, value):
        try:
            return float(value)
        except Exception:
            raise errors.LiteralParseFailure(self)

    def emit(self, codegen):
        codegen.emit_float(self.value)


class IntegerExpr(LiteralExpr):  # [TODO] Overflow handlers

    def __init__(self, location, value, signed, base):
        self.signed = signed
        self.base = base
        super().__init__(location, value)

    def _parse(self, value):
        try:
            return int(value, self.base)
        except Exception:
            raise errors.LiteralParseFailure(self)

    def emit(self, codegen):
        codegen.emit_integer(self.value)


class CallExpr(Expr):

    def __init__(self, location, function, arguments):
        super().__init__(location)
        self.function = function
        self.arguments = arguments

    def __repr__(self):
        return 'Call(%r, %r)' % (self.function, self.arguments)

    def emit(self, codegen):
        codegen.emit_call_expr(self)


class UnaryExpr(Expr):

    def __init__(self, location, operator, expr):
        super().__init__(location)
        self.operator = operator
        self.expr = expr

    def __repr__(self):
        return 'Unary(%r, %r)' % (self.operator, self.expr)

    def emit(self, codegen):
        codegen.emit_unary_expr(self)


class BinaryExpr(ASTNode):

    def __init__(self, location, operator, lhs, rhs):
        super().__init__(location)
        self.operator = operator
        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self):
        return 'Binary(%r, %r, %r)' % (self.operator, self.lhs, self.rhs)

    def emit(self, codegen):
        codegen.emit_binary_expr(self)

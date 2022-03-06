import ctypes
import decimal

from . import errors


class ASTNode:

    def __init__(self, location):
        self.location = location


class BaseExpr(ASTNode):
    pass


class LiteralExpr(BaseExpr):

    def __init__(self, location, raw_value, value):
        super().__init__(location)
        self.raw_value = raw_value
        self.value = value

    def __repr__(self):
        return f'{type(self).__name__}({repr(self.value)}'


class BooleanLiteralExpr(LiteralExpr):

    @classmethod
    def from_token(cls, token):
        if token.value == 'false':
            return cls(token.location.copy(), token.value, False)
        if token.value == 'true':
            return cls(token.location.copy(), token.value, True)
        raise errors.LiteralParseFailure(cls, token, 'Invalid value')


class RuneLiteralExpr(LiteralExpr):

    @classmethod
    def from_token(cls, token):
        if len(token.value) != 1:
            raise errors.LiteralParseFailure(cls, token, 'Length != 1')
        return cls(token.location.copy(), token.value, token.value)


class StringLiteralExpr(LiteralExpr):

    @classmethod
    def from_token(cls, token):
        return cls(token.location.copy(), token.value, token.value)


class NumericLiteralExpr(LiteralExpr):
    pass


class IntegerLiteralExpr(NumericLiteralExpr):

    def __init__(self, location, raw_value, value, signed, size, overflow):
        super().__init__(location, raw_value, value)
        self.signed = signed
        self.size = size
        self.overflow = overflow

    @classmethod
    def from_token(cls, token):
        try:
            value = int(token.value, token['base'])
        except Exception as e:
            raise errors.LiteralParseFailure(cls, token, str(e))

        if token['signedness'] == 'i':
            signed = True
        elif token['signedness'] == 'u':
            signed = False
        else:
            raise errors.LiteralParseFailure(cls, token, 'Invalid signedness')

        size = token.get('size')
        if size:
            try:
                size = int(size)
            except Exception:
                raise errors.LiteralParseFailure(
                    cls, token, 'Invalid size'
                ) from None
        else:
            size = ctypes.sizeof(ctypes.c_int) * 8

        if token['overflow'] == 'w':
            overflow = 'wrap'
        elif token['overflow'] == 'c':
            overflow = 'clamp'
        elif not token['overflow']:
            overflow = None
        else:
            raise errors.LiteralParseFailure(
                cls,
                token,
                'Invalid overflow handler'
            )

        return cls(
            token.location.copy(), token.value, value, signed, size, overflow
        )


class FloatLiteralExpr(NumericLiteralExpr):

    def __init__(self, location, raw_value, value, size, round):
        super().__init__(location, raw_value, value)
        self.size = size
        self.round = round

    @classmethod
    def from_token(cls, token):
        try:
            value = float(token.value)
        except Exception as e:
            raise errors.LiteralParseFailure(cls, token, str(e))

        size = token.get('size')
        if size:
            try:
                size = int(size)
            except Exception:
                raise (
                    errors.LiteralParseFailure(cls, token, 'Invalid size')
                ) from None
        else:
            size = ctypes.sizeof(ctypes.c_float) * 8

        if token['round'] == 'rn':
            round = 'nearest'
        elif token['round'] == 'ru':
            round = 'up'
        elif token['round'] == 'rd':
            round = 'down'
        elif token['round'] == 'rz':
            round = 'towards_zero'
        elif token['round'] == 'ra':
            round = 'away_from_zero'
        elif not token['round']:
            round = 'nearest'
        else:
            raise errors.LiteralParseFailure(
                cls,
                token,
                'Invalid rounding mode'
            )

        return cls(token.location.copy(), token.value, value, size, round)


class DecimalLiteralExpr(NumericLiteralExpr):

    def __init__(self, location, raw_value, value, round):
        super().__init__(location, raw_value, value)
        self.round = round

    @classmethod
    def from_token(cls, token):
        try:
            value = decimal.Decimal(token.value)
        except Exception as e:
            raise errors.LiteralParseFailure(cls, token, str(e))

        if token['round'] == 'rn':
            round = 'nearest'
        if token['round'] == 'ru':
            round = 'up'
        elif token['round'] == 'rd':
            round = 'down'
        elif token['round'] == 'rz':
            round = 'towards_zero'
        elif token['round'] == 'ra':
            round = 'away_from_zero'
        elif not token['round']:
            round = None
        else:
            raise errors.LiteralParseFailure(
                cls,
                token,
                'Invalid rounding mode'
            )

        return cls(token.location.copy(), token.value, value, round)


class CallExpr(BaseExpr):

    def __init__(self, location, function, arguments):
        super().__init__(location)
        self.function = function
        self.arguments = arguments

    def __repr__(self):
        return 'Call(%r, %r)' % (self.function, self.arguments)


class IndexExpr(BaseExpr):

    def __init__(self, location, indexable, index):
        super().__init__(location)
        self.indexable = indexable
        self.index = index

    def __repr__(self):
        return 'Index(%r, %r)' % (self.indexable, self.index)


class UnaryExpr(BaseExpr):

    def __init__(self, location, operator, expr):
        super().__init__(location)
        self.operator = operator
        self.expr = expr

    def __repr__(self):
        return 'Unary(%r, %r)' % (self.operator, self.expr)


class BinaryExpr(BaseExpr):

    def __init__(self, location, operator, lhs, rhs):
        super().__init__(location)
        self.operator = operator
        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self):
        return 'Binary(%r, %r, %r)' % (self.operator, self.lhs, self.rhs)


class LookupExpr(BaseExpr):

    def __init__(self, location, identifier):
        super().__init__(location)
        self.identifier = identifier

    def __repr__(self):
        return 'Lookup(%r)' % (self.identifier)


class ConstDefinition(ASTNode):

    def __init__(self, location, name, literal_expr):
        super().__init__(location)
        self.name = name
        self.literal_expr = literal_expr

    def __repr__(self):
        return 'ConstDefinition(%r, %r, %r)' % (
            self.location, self.name, self.literal_expr
        )


class Implementation(ASTNode):

    def __init__(self, location, interface, implementing_type, funcs):
        super().__init__(location)
        self.interface = interface
        self.implementing_type = implementing_type
        self.funcs = funcs

    def __repr__(self):
        return 'Implementation(%r, %r, %r, %r)' % (
            self.location, self.interface, self.implementing_type, self.funcs
        )


class DeferredLookup(ASTNode):

    def __init__(self, location, value):
        super().__init__(location)
        self.value = value

    def __repr__(self):
        return 'DeferredLookup(%r, %r)' % (self.location, self.value)


class If(ASTNode):

    def __init__(self, location, conditional_expr, code):
        super().__init__(location)
        self.conditional_expr = conditional_expr
        self.code = code


class Else(ASTNode):

    def __init__(self, location, block):
        super().__init__(location)
        self.block = block


class Loop(ASTNode):

    def __init__(self, location, code):
        super().__init__(location)
        self.code = code


class While(ASTNode):

    def __init__(self, location, conditional_expr, code):
        super().__init__(location)
        self.conditional_expr = conditional_expr
        self.code = code


class Break(ASTNode):
    pass


class Continue(ASTNode):
    pass


class Return(ASTNode):

    def __init__(self, location, expr):
        super().__init__(location)
        self.expr = expr

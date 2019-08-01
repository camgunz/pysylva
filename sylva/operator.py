from enum import Enum

from . import errors


class Associativity(Enum):
    Null = 0
    Left = 1
    Right = 2


class Arity(Enum):
    Unary = 1
    Binary = 2


class Operator(Enum):

    AttributeLookup = ('.', 14, Associativity.Left, Arity.Binary)
    ReflectionLookup = ('::', 14, Associativity.Left, Arity.Binary)
    AbsoluteValue = ('+', 13, Associativity.Right, Arity.Unary)
    FlipSign = ('-', 13, Associativity.Right, Arity.Unary)
    Not = ('!', 13, Associativity.Left, Arity.Unary)
    Exponent = ('**', 12, Associativity.Right, Arity.Binary)
    Multiply = ('*', 11, Associativity.Left, Arity.Binary)
    Divide = ('/', 11, Associativity.Left, Arity.Binary)
    IntegerDivide = ('//', 11, Associativity.Left, Arity.Binary)
    Remainder = ('%', 11, Associativity.Left, Arity.Binary)
    Add = ('+', 10, Associativity.Left, Arity.Binary)
    Subtract = ('-', 10, Associativity.Left, Arity.Binary)
    LeftShift = ('<<', 9, Associativity.Left, Arity.Binary)
    RightShiftSign = ('>>', 9, Associativity.Left, Arity.Binary)
    RightShiftZero = ('>>>', 9, Associativity.Left, Arity.Binary)
    BinaryAnd = ('&', 8, Associativity.Left, Arity.Binary)
    BinaryXOr = ('^', 7, Associativity.Left, Arity.Binary)
    BinaryOr = ('|', 6, Associativity.Left, Arity.Binary)
    BinaryNot = ('~', 5, Associativity.Right, Arity.Unary)
    LessThan = ('<', 4, Associativity.Left, Arity.Binary)
    LessThanOrEqual = ('<=', 4, Associativity.Left, Arity.Binary)
    GreaterThan = ('>', 4, Associativity.Left, Arity.Binary)
    GreaterThanOrEqual = ('>=', 4, Associativity.Left, Arity.Binary)
    Equal = ('==', 3, Associativity.Left, Arity.Binary)
    NotEqual = ('!=', 3, Associativity.Left, Arity.Binary)
    And = ('&&', 2, Associativity.Left, Arity.Binary)
    Or = ('||', 1, Associativity.Left, Arity.Binary)

    def __init__(self, symbol, precedence, associativity, arity):
        self.symbol = symbol
        self.precedence = precedence
        self.associativity = associativity
        self.arity = arity

    def __repr__(self):
        return 'Operator(%r, %r, %r, %r)' % (
            self.symbol,
            self.precedence,
            self.associativity,
            self.arity
        )

    def __str__(self):
        return f'<{self.name}Operator>'

    @classmethod
    def FromToken(cls, token, arity):
        ops = [
            op for op in cls.__members__
            if op.symbol == token.value
            and op.arity == arity
        ]
        if not ops:
            raise errors.NoOperatorForToken(token)
        if len(ops) > 1:
            raise errors.MultipleOperatorsForToken(token, ops)
        return ops[0]

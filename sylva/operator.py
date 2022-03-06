import enum


@enum.unique
class Operator(enum.Enum):

    AttributeLookup = ('.', 130)
    ReflectionLookup = ('::', 130)

    Exponent = ('**', 120)

    BinaryNot = ('~', 110)

    Multiply = ('*', 100)
    Divide = ('/', 100)
    Remainder = ('%', 100)

    Plus = ('+', 90, 110)
    Minus = ('-', 90, 110)

    LeftShift = ('<<', 80)
    RightShiftSign = ('>>', 80)
    RightShiftZero = ('>>>', 80)

    BinaryAnd = ('&', 70)

    BinaryXOr = ('^', 60)

    BinaryOr = ('|', 50)

    LessThan = ('<', 40)
    LessThanOrEqual = ('<=', 40)
    GreaterThan = ('>', 40)
    GreaterThanOrEqual = ('>=', 40)
    Equal = ('==', 40)
    NotEqual = ('!=', 40)

    Not = ('!', 30)

    And = ('&&', 20)

    Or = ('||', 10)

    def __init__(self, symbol, precedence, unary_precedence=None):
        self.symbol = symbol
        self.precedence = precedence
        self.unary_precedence = unary_precedence

    def __repr__(self):
        return 'Operator(%r, %r, %r)' % (
            self.symbol,
            self.precedence,
            self.unary_precedence,
        )

    def __str__(self):
        return f'<{self.name}Operator>'

    @classmethod
    def max_precedence(cls):
        return max(*(o.precedence for o in cls.__members__.values()))

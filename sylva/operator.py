import enum


@enum.unique
class Operator(enum.Enum):

    def __init__(self, value, arity):
        self._value_ = (value, arity)
        self.arity = arity
        self.is_assignment = value.endswith('=')

    AttributeLookup = ('.', 2)
    ReflectionLookup = ('::', 2)
    # Index = ('[', 2)
    Assign = ('=', 2)
    Exponent = ('**', 2)
    ExponentAssign = ('**=', 2)
    BinaryNot = ('~', 1)
    Multiply = ('*', 2)
    MultiplyAssign = ('*=', 2)
    Divide = ('/', 2)
    DivideAssign = ('/=', 2)
    FloorDivide = ('//', 2)
    FloorDivideAssign = ('//=', 2)
    Modulo = ('%', 2)
    ModuloAssign = ('%=', 2)
    AbsoluteValue = ('+', 1)
    Add = ('+', 2)
    FlipSign = ('-', 1)
    Subtract = ('-', 2)
    ShiftLeft = ('<<', 2)
    ShiftLeftAssign = ('<<=', 2)
    RightShift = ('>>', 2)
    RightShiftAssign = ('>>=', 2)
    UnsignedRightShift = ('>>>', 2)
    UnsignedRightShiftAssign = ('>>>=', 2)
    BinaryAnd = ('&', 2)
    BinaryAndAssign = ('&=', 2)
    BinaryXOr = ('^', 2)
    BinaryXOrAssign = ('^=', 2)
    BinaryOr = ('|', 2)
    BinaryOrAssign = ('|=', 2)
    LessThan = ('<', 2)
    LessThanOrEqual = ('<=', 2)
    GreaterThan = ('>', 2)
    GreaterThanOrEqual = ('>=', 2)
    Equals = ('==', 2)
    NotEquals = ('!=', 2)
    BooleanNot = ('!', 1)
    BooleanAnd = ('&&', 2)
    BooleanAndAssign = ('&&=', 2)
    BooleanOr = ('||', 2)
    BooleanOrAssign = ('||=', 2)

    @classmethod
    def lookup(cls, value, arity):
        for op in cls.__members__.values():
            if op.value == (value, arity):
                return op

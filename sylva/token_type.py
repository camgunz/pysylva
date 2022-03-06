from .operator import *
from .token_category import TokenCategory


class TokenType:

    def __init__(self, name, categories, operator=None, syntax_sugar=None):
        self.name = name
        self.categories = categories
        self.operator = operator
        self.syntax_sugar = syntax_sugar

    def __repr__(self):
        return 'TokenType(%r, %r, %r, %r)' % (
            self.name,
            self.categories,
            self.operator,
            self.syntax_sugar
        )

    def __str__(self):
        return f'<TokenType {self.name}>'

Unknown = TokenType('Unknown', {TokenCategory.Unknown})
Comment = TokenType('Comment', {TokenCategory.Comment})
Value = TokenType('Value', {TokenCategory.Value})
Module = TokenType('Module', {TokenCategory.Keyword})
Requirement = TokenType('Requirement', {TokenCategory.Keyword})
Fn = TokenType('Fn', {TokenCategory.Keyword})
FnType = TokenType('FnType', {TokenCategory.Keyword})
Struct = TokenType('Struct', {TokenCategory.Keyword})
Variant = TokenType('Variant', {TokenCategory.Keyword})
CFn = TokenType('CFn', {TokenCategory.Keyword})
CFnType = TokenType('CFnType', {TokenCategory.Keyword})
CStruct = TokenType('CStruct', {TokenCategory.Keyword})
CUnion = TokenType('CUnion', {TokenCategory.Keyword})
Enum = TokenType('Enum', {TokenCategory.Keyword})
Range = TokenType('Range', {TokenCategory.Keyword})
Alias = TokenType('Alias', {TokenCategory.Keyword})
Implementation = TokenType('Implementation', {TokenCategory.Keyword})
Interface = TokenType('Interface', {TokenCategory.Keyword})
Const = TokenType('Const', {TokenCategory.Keyword})
Var = TokenType('Var', {TokenCategory.Keyword})
If = TokenType('If', {TokenCategory.Keyword})
Else = TokenType('Else', {TokenCategory.Keyword})
Match = TokenType('Match', {TokenCategory.Keyword})
Switch = TokenType('Switch', {TokenCategory.Keyword})
Case = TokenType('Case', {TokenCategory.Keyword})
Default = TokenType('Default', {TokenCategory.Keyword})
For = TokenType('For', {TokenCategory.Keyword})
Loop = TokenType('Loop', {TokenCategory.Keyword})
While = TokenType('While', {TokenCategory.Keyword})
Break = TokenType('Break', {TokenCategory.Keyword})
Continue = TokenType('Continue', {TokenCategory.Keyword})
Return = TokenType('Return', {TokenCategory.Keyword})
Boolean = TokenType('Boolean', {TokenCategory.Boolean})
Rune = TokenType('Rune', {TokenCategory.Rune})
String = TokenType('String', {TokenCategory.String})
Integer = TokenType('Integer', {TokenCategory.Number, TokenCategory.Integer})
Float = TokenType('Float', {TokenCategory.Number, TokenCategory.Float})
Decimal = TokenType('Decimal', {TokenCategory.Number, TokenCategory.Decimal})
Space = TokenType('Space', {TokenCategory.Blank})
LineBreak = TokenType('LineBreak', {TokenCategory.Blank})
OpenParen = TokenType('OpenParen', {TokenCategory.Symbol})
CloseParen = TokenType('CloseParen', {TokenCategory.Symbol})
OpenBracket = TokenType('OpenBracket', {TokenCategory.Symbol})
CloseBracket = TokenType('CloseBracket', {TokenCategory.Symbol})
OpenBrace = TokenType('OpenBrace', {TokenCategory.Symbol})
CloseBrace = TokenType('CloseBrace', {TokenCategory.Symbol})
Comma = TokenType('Comma', {TokenCategory.Symbol})
Colon = TokenType('Colon', {TokenCategory.Symbol})
Semicolon = TokenType('Semicolon', {TokenCategory.Symbol})
Ellipsis = TokenType('Ellipsis', {TokenCategory.Symbol})
Equal = TokenType('Equal', {TokenCategory.Symbol})
Plus = TokenType(
    'Plus',
    {TokenCategory.Symbol, TokenCategory.Operator},
    Operator.Plus
)
PlusEqual = TokenType(
    'PlusEqual',
    {
        TokenCategory.Symbol, TokenCategory.Operator,
        TokenCategory.SyntaxSugar
    },
    syntax_sugar=[Equal, '<prev>', Plus]
)
DoublePlus = TokenType(
    'DoublePlus',
    {
        TokenCategory.Symbol, TokenCategory.Operator,
        TokenCategory.SyntaxSugar
    },
    syntax_sugar=[Equal, '<prev>', Plus, '<one>']
)
Minus = TokenType(
    'Minus',
    {TokenCategory.Symbol, TokenCategory.Operator},
    Operator.Minus
)
MinusEqual = TokenType(
    'MinusEqual',
    {
        TokenCategory.Symbol, TokenCategory.Operator,
        TokenCategory.SyntaxSugar
    },
    syntax_sugar=[Equal, '<prev>', Minus]
)
DoubleMinus = TokenType(
    'DoubleMinus',
    {
        TokenCategory.Symbol, TokenCategory.Operator,
        TokenCategory.SyntaxSugar
    },
    syntax_sugar=[Equal, '<prev>', Minus, '<one>']
)
Tilde = TokenType(
    'Tilde',
    {TokenCategory.Symbol, TokenCategory.Operator},
    Operator.BinaryNot
)
DoublePipe = TokenType(
    'DoublePipe',
    {TokenCategory.Symbol, TokenCategory.Operator},
    Operator.Or
)
DoubleAmpersand = TokenType(
    'DoubleAmpersand',
    {TokenCategory.Symbol, TokenCategory.Operator},
    Operator.And
)
Bang = TokenType(
    'Bang',
    {TokenCategory.Symbol, TokenCategory.Operator},
    Operator.Not
)
DoubleEqual = TokenType(
    'DoubleEqual',
    {TokenCategory.Symbol, TokenCategory.Operator},
    Operator.Equal
)
BangEqual = TokenType(
    'BangEqual',
    {TokenCategory.Symbol, TokenCategory.Operator},
    Operator.NotEqual
)
OpenAngleEqual = TokenType(
    'OpenAngleEqual',
    {TokenCategory.Symbol, TokenCategory.Operator},
    Operator.GreaterThanOrEqual
)
OpenAngle = TokenType(
    'OpenAngle',
    {TokenCategory.Symbol, TokenCategory.Operator},
    Operator.GreaterThan
)
CloseAngleEqual = TokenType(
    'CloseAngleEqual',
    {TokenCategory.Symbol, TokenCategory.Operator},
    Operator.LessThanOrEqual
)
CloseAngle = TokenType(
    'CloseAngle',
    {TokenCategory.Symbol, TokenCategory.Operator},
    Operator.LessThan
)
Pipe = TokenType(
    'Pipe',
    {TokenCategory.Symbol, TokenCategory.Operator},
    Operator.BinaryOr
)
PipeEqual = TokenType(
    'PipeEqual',
    {
        TokenCategory.Symbol, TokenCategory.Operator,
        TokenCategory.SyntaxSugar
    },
    syntax_sugar=[Equal, '<prev>', Pipe]
)
Caret = TokenType(
    'Caret',
    {TokenCategory.Symbol, TokenCategory.Operator},
    Operator.BinaryXOr
)
CaretEqual = TokenType(
    'CaretEqual',
    {
        TokenCategory.Symbol, TokenCategory.Operator,
        TokenCategory.SyntaxSugar
    },
    syntax_sugar=[Equal, '<prev>', Caret]
)
Ampersand = TokenType(
    'Ampersand',
    {TokenCategory.Symbol, TokenCategory.Operator},
    Operator.BinaryAnd
)
AmpersandEqual = TokenType(
    'AmpersandEqual',
    {
        TokenCategory.Symbol, TokenCategory.Operator,
        TokenCategory.SyntaxSugar
    },
    syntax_sugar=[Equal, '<prev>', Ampersand]
)
TripleCloseAngle = TokenType(
    'TripleCloseAngle',
    {TokenCategory.Symbol, TokenCategory.Operator},
    Operator.RightShiftZero
)
TripleCloseAngleEqual = TokenType(
    'TripleCloseAngleEqual',
    {
        TokenCategory.Symbol, TokenCategory.Operator,
        TokenCategory.SyntaxSugar
    },
    syntax_sugar=[Equal, '<prev>', TripleCloseAngle]
)
DoubleCloseAngle = TokenType(
    'DoubleCloseAngle',
    {TokenCategory.Symbol, TokenCategory.Operator},
    Operator.RightShiftSign
)
DoubleCloseAngleEqual = TokenType(
    'DoubleCloseAngleEqual',
    {
        TokenCategory.Symbol, TokenCategory.Operator,
        TokenCategory.SyntaxSugar
    },
    syntax_sugar=[Equal, '<prev>', DoubleCloseAngle]
)
DoubleOpenAngle = TokenType(
    'DoubleOpenAngle',
    {TokenCategory.Symbol, TokenCategory.Operator},
    Operator.LeftShift
)
DoubleOpenAngleEqual = TokenType(
    'DoubleOpenAngleEqual',
    {
        TokenCategory.Symbol, TokenCategory.Operator,
        TokenCategory.SyntaxSugar
    },
    syntax_sugar=[Equal, '<prev>', DoubleOpenAngle]
)
Star = TokenType(
    'Star',
    {TokenCategory.Symbol, TokenCategory.Operator},
    Operator.Multiply
)
StarEqual = TokenType(
    'StarEqual',
    {
        TokenCategory.Symbol, TokenCategory.Operator,
        TokenCategory.SyntaxSugar
    },
    syntax_sugar=[Equal, '<prev>', Star]
)
Slash = TokenType(
    'Slash',
    {TokenCategory.Symbol, TokenCategory.Operator},
    Operator.Divide
)
SlashEqual = TokenType(
    'SlashEqual',
    {
        TokenCategory.Symbol, TokenCategory.Operator,
        TokenCategory.SyntaxSugar
    },
    syntax_sugar=[Equal, '<prev>', Slash]
)
Percent = TokenType(
    'Percent',
    {TokenCategory.Symbol, TokenCategory.Operator},
    Operator.Remainder
)
PercentEqual = TokenType(
    'PercentEqual',
    {
        TokenCategory.Symbol, TokenCategory.Operator,
        TokenCategory.SyntaxSugar
    },
    syntax_sugar=[Equal, '<prev>', Percent]
)
DoubleStar = TokenType(
    'DoubleStar',
    {TokenCategory.Symbol, TokenCategory.Operator},
    Operator.Exponent
)
DoubleStarEqual = TokenType(
    'DoubleStarEqual',
    {
        TokenCategory.Symbol, TokenCategory.Operator,
        TokenCategory.SyntaxSugar
    },
    syntax_sugar=[Equal, '<prev>', DoubleStar]
)
Dot = TokenType(
    'Dot',
    {TokenCategory.Symbol, TokenCategory.Operator},
    Operator.AttributeLookup
)
DoubleColon = TokenType(
    'DoubleColon',
    {TokenCategory.Symbol, TokenCategory.Operator},
    Operator.ReflectionLookup
)

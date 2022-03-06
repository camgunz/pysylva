import enum


@enum.unique
class TokenCategory(enum.Enum):

    Unknown = 'Unknown'
    Comment = 'Comment'
    Value = 'Value'
    Keyword = 'Keyword'
    Boolean = 'Boolean'
    Rune = 'Rune'
    String = 'String'
    Number = 'Number'
    Decimal = 'Decimal'
    Float = 'Float'
    Integer = 'Integer'
    Blank = 'Blank'
    Symbol = 'Symbol'
    Operator = 'Operator'
    SyntaxSugar = 'SyntaxSugar'

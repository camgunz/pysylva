import enum

from collections import namedtuple


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


class MetaTokenType(type):

    def __repr__(cls):
        return 'TokenType(%s, %s, %s)' % (
            cls.name,
            cls.categories,
            cls.has_value
        )

    def __str__(cls):
        return f'<TokenType {cls.name}>'


class TokenType:

    class Unknown(metaclass=MetaTokenType):
        name = 'Unknown'
        categories = {TokenCategory.Unknown}
        has_value = True

    class Comment(metaclass=MetaTokenType):
        name = 'Comment'
        categories = {TokenCategory.Comment}
        has_value = True

    class Value(metaclass=MetaTokenType):
        name = 'Value'
        categories = {TokenCategory.Value}
        has_value = True

    class Module(metaclass=MetaTokenType):
        name = 'Module'
        categories = {TokenCategory.Keyword}
        has_value = False

    class Requirement(metaclass=MetaTokenType):
        name = 'Requirement'
        categories = {TokenCategory.Keyword}
        has_value = False

    class Fn(metaclass=MetaTokenType):
        name = 'Fn'
        categories = {TokenCategory.Keyword}
        has_value = False

    class FnType(metaclass=MetaTokenType):
        name = 'FnType'
        categories = {TokenCategory.Keyword}
        has_value = False

    class Array(metaclass=MetaTokenType):
        name = 'Array'
        categories = {TokenCategory.Keyword}
        has_value = False

    class Struct(metaclass=MetaTokenType):
        name = 'Struct'
        categories = {TokenCategory.Keyword}
        has_value = False

    class Variant(metaclass=MetaTokenType):
        name = 'Variant'
        categories = {TokenCategory.Keyword}
        has_value = False

    class CFn(metaclass=MetaTokenType):
        name = 'CFn'
        categories = {TokenCategory.Keyword}
        has_value = False

    class CFnType(metaclass=MetaTokenType):
        name = 'CFnType'
        categories = {TokenCategory.Keyword}
        has_value = False

    class CStruct(metaclass=MetaTokenType):
        name = 'CStruct'
        categories = {TokenCategory.Keyword}
        has_value = False

    class CUnion(metaclass=MetaTokenType):
        name = 'CUnion'
        categories = {TokenCategory.Keyword}
        has_value = False

    class Enum(metaclass=MetaTokenType):
        name = 'Enum'
        categories = {TokenCategory.Keyword}
        has_value = False

    class Range(metaclass=MetaTokenType):
        name = 'Range'
        categories = {TokenCategory.Keyword}
        has_value = False

    class Alias(metaclass=MetaTokenType):
        name = 'Alias'
        categories = {TokenCategory.Keyword}
        has_value = False

    class Implementation(metaclass=MetaTokenType):
        name = 'Implementation'
        categories = {TokenCategory.Keyword}
        has_value = False

    class Interface(metaclass=MetaTokenType):
        name = 'Interface'
        categories = {TokenCategory.Keyword}
        has_value = False

    class Const(metaclass=MetaTokenType):
        name = 'Const'
        categories = {TokenCategory.Keyword}
        has_value = False

    class Var(metaclass=MetaTokenType):
        name = 'Var'
        categories = {TokenCategory.Keyword}
        has_value = False

    class If(metaclass=MetaTokenType):
        name = 'If'
        categories = {TokenCategory.Keyword}
        has_value = False

    class Else(metaclass=MetaTokenType):
        name = 'Else'
        categories = {TokenCategory.Keyword}
        has_value = False

    class Match(metaclass=MetaTokenType):
        name = 'Match'
        categories = {TokenCategory.Keyword}
        has_value = False

    class Switch(metaclass=MetaTokenType):
        name = 'Switch'
        categories = {TokenCategory.Keyword}
        has_value = False

    class Case(metaclass=MetaTokenType):
        name = 'Case'
        categories = {TokenCategory.Keyword}
        has_value = False

    class Default(metaclass=MetaTokenType):
        name = 'Default'
        categories = {TokenCategory.Keyword}
        has_value = False

    class For(metaclass=MetaTokenType):
        name = 'For'
        categories = {TokenCategory.Keyword}
        has_value = False

    class Loop(metaclass=MetaTokenType):
        name = 'Loop'
        categories = {TokenCategory.Keyword}
        has_value = False

    class While(metaclass=MetaTokenType):
        name = 'While'
        categories = {TokenCategory.Keyword}
        has_value = False

    class Break(metaclass=MetaTokenType):
        name = 'Break'
        categories = {TokenCategory.Keyword}
        has_value = False

    class Continue(metaclass=MetaTokenType):
        name = 'Continue'
        categories = {TokenCategory.Keyword}
        has_value = False

    class Error(metaclass=MetaTokenType):
        name = 'Error'
        categories = {TokenCategory.Keyword}
        has_value = False

    class Fallthrough(metaclass=MetaTokenType):
        name = 'Fallthrough'
        categories = {TokenCategory.Keyword}
        has_value = False

    class Return(metaclass=MetaTokenType):
        name = 'Return'
        categories = {TokenCategory.Keyword}
        has_value = False

    class With(metaclass=MetaTokenType):
        name = 'With'
        categories = {TokenCategory.Keyword}
        has_value = False

    class Boolean(metaclass=MetaTokenType):
        name = 'Boolean'
        categories = {TokenCategory.Boolean}
        has_value = True

    class Rune(metaclass=MetaTokenType):
        name = 'Rune'
        categories = {TokenCategory.Rune}
        has_value = True

    class String(metaclass=MetaTokenType):
        name = 'String'
        categories = {TokenCategory.String}
        has_value = True

    class Decimal(metaclass=MetaTokenType):
        name = 'Decimal'
        categories = {TokenCategory.Decimal}
        has_value = True

    class Float(metaclass=MetaTokenType):
        name = 'Float'
        categories = {TokenCategory.Float}
        has_value = True

    class SignedBinInteger(metaclass=MetaTokenType):
        name = 'SignedBinInteger'
        categories = {TokenCategory.Number, TokenCategory.Integer}
        has_value = True
        signed = True
        base = 2

    class UnsignedBinInteger(metaclass=MetaTokenType):
        name = 'UnsignedBinInteger'
        categories = {TokenCategory.Number, TokenCategory.Integer}
        has_value = True
        signed = False
        base = 2

    class SignedOctInteger(metaclass=MetaTokenType):
        name = 'SignedOctInteger'
        categories = {TokenCategory.Number, TokenCategory.Integer}
        has_value = True
        signed = True
        base = 8

    class UnsignedOctInteger(metaclass=MetaTokenType):
        name = 'UnsignedOctInteger'
        categories = {TokenCategory.Number, TokenCategory.Integer}
        has_value = True
        signed = False
        base = 8

    class SignedDecInteger(metaclass=MetaTokenType):
        name = 'SignedDecInteger'
        categories = {TokenCategory.Number, TokenCategory.Integer}
        has_value = True
        signed = True
        base = 10

    class UnsignedDecInteger(metaclass=MetaTokenType):
        name = 'UnsignedDecInteger'
        categories = {TokenCategory.Number, TokenCategory.Integer}
        has_value = True
        signed = False
        base = 10

    class SignedHexInteger(metaclass=MetaTokenType):
        name = 'SignedHexInteger'
        categories = {TokenCategory.Number, TokenCategory.Integer}
        has_value = True
        signed = True
        base = 16

    class UnsignedHexInteger(metaclass=MetaTokenType):
        name = 'UnsignedHexInteger'
        categories = {TokenCategory.Number, TokenCategory.Integer}
        has_value = True
        signed = True
        base = 16

    class Space(metaclass=MetaTokenType):
        name = 'Space'
        categories = {TokenCategory.Blank}
        has_value = False

    class LineBreak(metaclass=MetaTokenType):
        name = 'LineBreak'
        categories = {TokenCategory.Blank}
        has_value = False

    class OpenParen(metaclass=MetaTokenType):
        name = 'OpenParen'
        categories = {TokenCategory.Symbol}
        has_value = False

    class CloseParen(metaclass=MetaTokenType):
        name = 'CloseParen'
        categories = {TokenCategory.Symbol}
        has_value = False

    class OpenBracket(metaclass=MetaTokenType):
        name = 'OpenBracket'
        categories = {TokenCategory.Symbol}
        has_value = False

    class CloseBracket(metaclass=MetaTokenType):
        name = 'CloseBracket'
        categories = {TokenCategory.Symbol}
        has_value = False

    class OpenBrace(metaclass=MetaTokenType):
        name = 'OpenBrace'
        categories = {TokenCategory.Symbol}
        has_value = False

    class CloseBrace(metaclass=MetaTokenType):
        name = 'CloseBrace'
        categories = {TokenCategory.Symbol}
        has_value = False

    class Comma(metaclass=MetaTokenType):
        name = 'Comma'
        categories = {TokenCategory.Symbol}
        has_value = False

    class Colon(metaclass=MetaTokenType):
        name = 'Colon'
        categories = {TokenCategory.Symbol}
        has_value = False

    class Arrow(metaclass=MetaTokenType):
        name = 'Arrow'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class Errow(metaclass=MetaTokenType):
        name = 'Errow'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class Plus(metaclass=MetaTokenType):
        name = 'Plus'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = True
        binary = True

    class PlusAssign(metaclass=MetaTokenType):
        name = 'AddAssign'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class Increment(metaclass=MetaTokenType):
        name = 'Increment'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class Minus(metaclass=MetaTokenType):
        name = 'Minus'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = True
        binary = True

    class MinusAssign(metaclass=MetaTokenType):
        name = 'SubtractAssign'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class Decrement(metaclass=MetaTokenType):
        name = 'Decrement'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class Tilde(metaclass=MetaTokenType):
        name = 'Tilde'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = True
        binary = False

    class Assign(metaclass=MetaTokenType):
        name = 'Assign'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class BooleanOr(metaclass=MetaTokenType):
        name = 'BooleanOr'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class BooleanAnd(metaclass=MetaTokenType):
        name = 'BooleanAnd'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class BooleanNot(metaclass=MetaTokenType):
        name = 'BooleanNot'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = True
        binary = False

    class Equal(metaclass=MetaTokenType):
        name = 'Equal'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class IdentityEqual(metaclass=MetaTokenType):
        name = 'IdentityEqual'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class NotEqual(metaclass=MetaTokenType):
        name = 'NotEqual'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class IdentityNotEqual(metaclass=MetaTokenType):
        name = 'IdentityNotEqual'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class GreaterThanOrEqual(metaclass=MetaTokenType):
        name = 'GreaterThanOrEqual'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class GreaterThan(metaclass=MetaTokenType):
        name = 'GreaterThan'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class LessThanOrEqual(metaclass=MetaTokenType):
        name = 'LessThanOrEqual'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class LessThan(metaclass=MetaTokenType):
        name = 'LessThan'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class BinaryOr(metaclass=MetaTokenType):
        name = 'BinaryOr'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class BinaryOrAssign(metaclass=MetaTokenType):
        name = 'BinaryOrAssign'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class BinaryXor(metaclass=MetaTokenType):
        name = 'BinaryXor'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class BinaryXorAssign(metaclass=MetaTokenType):
        name = 'BinaryXorAssign'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class BinaryAnd(metaclass=MetaTokenType):
        name = 'BinaryAnd'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class BinaryAndAssign(metaclass=MetaTokenType):
        name = 'BinaryAndAssign'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class UnsignedRightShift(metaclass=MetaTokenType):
        name = 'UnsignedRightShift'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class UnsignedRightShiftAssign(metaclass=MetaTokenType):
        name = 'UnsignedRightShiftAssign'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class RightShift(metaclass=MetaTokenType):
        name = 'RightShift'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class RightShiftAssign(metaclass=MetaTokenType):
        name = 'RightShiftAssign'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class LeftShift(metaclass=MetaTokenType):
        name = 'LeftShift'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class LeftShiftAssign(metaclass=MetaTokenType):
        name = 'LeftShiftAssign'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class Subtract(metaclass=MetaTokenType):
        name = 'Subtract'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class Multiply(metaclass=MetaTokenType):
        name = 'Multiply'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class MultiplyAssign(metaclass=MetaTokenType):
        name = 'MultiplyAssign'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class Divide(metaclass=MetaTokenType):
        name = 'Divide'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class DivideAssign(metaclass=MetaTokenType):
        name = 'DivideAssign'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class IntegerDivide(metaclass=MetaTokenType):
        name = 'IntegerDivide'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class IntegerDivideAssign(metaclass=MetaTokenType):
        name = 'IntegerDivideAssign'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class Remainder(metaclass=MetaTokenType):
        name = 'Remainder'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class RemainderAssign(metaclass=MetaTokenType):
        name = 'RemainderAssign'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class BinaryNot(metaclass=MetaTokenType):
        name = 'BinaryNot'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = True
        binary = False

    class Exponent(metaclass=MetaTokenType):
        name = 'Exponent'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class ExponentAssign(metaclass=MetaTokenType):
        name = 'ExponentAssign'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class AttributeLookup(metaclass=MetaTokenType):
        name = 'AttributeLookup'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True

    class ReflectionLookup(metaclass=MetaTokenType):
        name = 'ReflectionLookup'
        categories = {TokenCategory.Symbol, TokenCategory.Operator}
        has_value = False
        unary = False
        binary = True


class Token:

    __slots__ = ('location', 'token_type', 'value')

    def __init__(self, location, token_type, value=None):
        self.location = location
        self.token_type = token_type
        self.value = value

    @property
    def categories(self):
        return self.token_type.categories

    @property
    def has_value(self):
        return self.token_type.has_value

    def __repr__(self):
        if self.has_value:
            return 'Token(%r, %r, %r)' % (
                self.location, self.token_type, self.value
            )
        return 'Token(%r, %r)' % (self.location, self.token_type)

    def __str__(self):
        if self.has_value:
            return f'<{self.token_type.name}Token {self.value}>'
        return f'<{self.token_type.name}Token>'

    def matches(self, token_types=None, token_categories=None):
        return (
            (token_types and self.token_type in token_types) or
            (token_categories and
                self.categories.intersection(token_categories))
        )

    def matches_types(self, token_types):
        return self.matches(token_types=token_types)

    def matches_categories(self, token_categories):
        return self.matches(token_categories=token_categories)

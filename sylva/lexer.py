import re

from . import debug
from . import errors
from .location import Location
from .token import Token, TokenCategory, TokenType


class TokenMatcher:

    __slots__ = ('regex', 'token_type', 'group_index', 'extra_skip')

    def __init__(self, rstr, token_type, group_index=0, extra_skip=0, flags=0):
        self.regex = re.compile(rstr, flags=flags)
        self.token_type = token_type
        self.group_index = group_index
        self.extra_skip = extra_skip

TOKEN_MATCHERS = [
    TokenMatcher(r"^#(.*)(\r\n|\r|\n)", TokenType.Comment),
    TokenMatcher(r"^( |\t)+", TokenType.Space),
    TokenMatcher(r"^(\r\n|\r|\n)", TokenType.LineBreak),

    TokenMatcher(
        r'^[+-]??\d+i(8|16|32|64|128)?(w|c)*',
        TokenType.SignedDecInteger
    ),
    TokenMatcher(
        r'^[+-]??\d+u(8|16|32|64|128)?(w|c)*',
        TokenType.UnsignedDecInteger
    ),

    TokenMatcher(
        r'^[+-]??\d+\.\d+([Ee][+-]??\d+)?f(16|32|64|128)(ru|rd|rz|ra)*',
        TokenType.Float
    ),
    TokenMatcher(
        r'^[+-]??\d+\.([Ee][+-]??\d+)?f(16|32|64|128)(ru|rd|rz|ra)*',
        TokenType.Float
    ),
    TokenMatcher(
        r'^[+-]??\d+([Ee][+-]??\d+)?f(16|32|64|128)(ru|rd|rz|ra)*',
        TokenType.Float
    ),
    TokenMatcher(
        r'^[+-]??\.\d+([Ee][+-]??\d+)?f(16|32|64|128)(ru|rd|rz|ra)*',
        TokenType.Float
    ),

    TokenMatcher(
        r'^inff(16|32|64|128)(ru|rd|rz|ra)*',
        TokenType.Float,
        flags=re.I,
    ),

    TokenMatcher(
        r'^nanf(16|32|64|128)(ru|rd|rz|ra)*',
        TokenType.Float,
        flags=re.I,
    ),

    TokenMatcher(
        r'^inf(ru|rd|rz|ra)*',
        TokenType.Decimal,
        flags=re.I,
    ),

    TokenMatcher(
        r'^nan(ru|rd|rz|ra)*',
        TokenType.Decimal,
        flags=re.I,
    ),

    TokenMatcher(
        r"^(0[Bb][01]+)i\d*", TokenType.SignedBinInteger, 1, 1
    ),
    TokenMatcher(
        r"^(0[Bb][01]+)u\d*", TokenType.UnsignedBinInteger, 1, 1
    ),
    TokenMatcher(r"^0[Bb][01]+", TokenType.Decimal),
    TokenMatcher(
        r"^(0[Oo][01234567]+)i", TokenType.SignedOctInteger, 1, 1
    ),
    TokenMatcher(
        r"^(0[Oo][01234567]+)u", TokenType.UnsignedOctInteger, 1, 1
    ),
    TokenMatcher(r"^0[Oo][01234567]+", TokenType.Decimal),
    TokenMatcher(
        r"^(0[Xx][0123456789aAbBcCdDeEfF]+)i",
        TokenType.SignedHexInteger,
        1,
        1
    ),
    TokenMatcher(
        r"^(0[Xx][0123456789aAbBcCdDeEfF]+)u",
        TokenType.UnsignedHexInteger,
        1,
        1
    ),
    TokenMatcher(
        r"^0[Xx][0123456789aAbBcCdDeEfF]+", TokenType.Decimal
    ),

    TokenMatcher(r'"(.*?)"', TokenType.String, 1, 2),
    TokenMatcher(r"^'(.*?)'", TokenType.Rune, 1, 2),
    TokenMatcher(r"^(true)\W", TokenType.Boolean, 1),
    TokenMatcher(r"^(false)\W", TokenType.Boolean, 1),
    TokenMatcher(r"^\(", TokenType.OpenParen),
    TokenMatcher(r"^\)", TokenType.CloseParen),
    TokenMatcher(r"^\[", TokenType.OpenBracket),
    TokenMatcher(r"^]", TokenType.CloseBracket),
    TokenMatcher(r"^{", TokenType.OpenBrace),
    TokenMatcher(r"^}", TokenType.CloseBrace),
    TokenMatcher(r"^,", TokenType.Comma),
    TokenMatcher(r"^`", TokenType.Tilde),
    TokenMatcher(r"^\|\|", TokenType.BooleanOr),
    TokenMatcher(r"^\|=", TokenType.BinaryOrAssign),
    TokenMatcher(r"^\|", TokenType.BinaryOr),
    TokenMatcher(r"^&&", TokenType.BooleanAnd),
    TokenMatcher(r"^&=", TokenType.BinaryAndAssign),
    TokenMatcher(r"^&", TokenType.BinaryAnd),
    TokenMatcher(r"^===", TokenType.IdentityEqual),
    TokenMatcher(r"^==", TokenType.Equal),
    TokenMatcher(r"^=", TokenType.Assign),
    TokenMatcher(r"^!==", TokenType.IdentityNotEqual),
    TokenMatcher(r"^!=", TokenType.NotEqual),
    TokenMatcher(r"^!", TokenType.BooleanNot),
    TokenMatcher(r"^\^=", TokenType.BinaryXorAssign),
    TokenMatcher(r"^\^", TokenType.BinaryXor),
    TokenMatcher(r"^>>>=", TokenType.UnsignedRightShiftAssign),
    TokenMatcher(r"^>>>", TokenType.UnsignedRightShift),
    TokenMatcher(r"^>>=", TokenType.RightShiftAssign),
    TokenMatcher(r"^>>", TokenType.RightShift),
    TokenMatcher(r"^>=", TokenType.GreaterThanOrEqual),
    TokenMatcher(r"^>", TokenType.GreaterThan),
    TokenMatcher(r"^<<=", TokenType.LeftShiftAssign),
    TokenMatcher(r"^<<", TokenType.LeftShift),
    TokenMatcher(r"^<=", TokenType.LessThanOrEqual),
    TokenMatcher(r"^<", TokenType.LessThan),
    TokenMatcher(r"^\+\+", TokenType.Increment),
    TokenMatcher(r"^\+=", TokenType.PlusAssign),
    TokenMatcher(r"^\+", TokenType.Plus),
    TokenMatcher(r"^--", TokenType.Decrement),
    TokenMatcher(r"^-=", TokenType.MinusAssign),
    TokenMatcher(r"^-", TokenType.Minus),
    TokenMatcher(r"^\*\*=", TokenType.ExponentAssign),
    TokenMatcher(r"^\*\*", TokenType.Exponent),
    TokenMatcher(r"^\*=", TokenType.MultiplyAssign),
    TokenMatcher(r"^\*", TokenType.Multiply),
    TokenMatcher(r"^//=", TokenType.IntegerDivideAssign),
    TokenMatcher(r"^//", TokenType.IntegerDivide),
    TokenMatcher(r"^/=", TokenType.DivideAssign),
    TokenMatcher(r"^/", TokenType.Divide),
    TokenMatcher(r"^%=", TokenType.RemainderAssign),
    TokenMatcher(r"^%", TokenType.Remainder),
    TokenMatcher(r"^~", TokenType.BinaryNot),
    TokenMatcher(r"^\.", TokenType.AttributeLookup),
    TokenMatcher(r"^::", TokenType.ReflectionLookup),
    TokenMatcher(r"^:", TokenType.Colon),

    TokenMatcher(r"^(module)\W", TokenType.Module, 1),
    TokenMatcher(r"^(requirement)\W", TokenType.Requirement, 1),
    TokenMatcher(r"^(fn)\W", TokenType.Fn, 1),
    TokenMatcher(r"^(fntype)\W", TokenType.FnType, 1),
    TokenMatcher(r"^(array)\W", TokenType.Array, 1),
    TokenMatcher(r"^(struct)\W", TokenType.Struct, 1),
    TokenMatcher(r"^(variant)\W", TokenType.Variant, 1),
    TokenMatcher(r"^(enum)\W", TokenType.Enum, 1),
    TokenMatcher(r"^(range)\W", TokenType.Range, 1),

    TokenMatcher(r"^(cfn)\W", TokenType.CFn, 1),
    TokenMatcher(r"^(cfntype)\W", TokenType.CFnType, 1),
    TokenMatcher(r"^(cstruct)\W", TokenType.CStruct, 1),
    TokenMatcher(r"^(cunion)\W", TokenType.CUnion, 1),

    TokenMatcher(r"^(alias)\W", TokenType.Alias, 1),
    TokenMatcher(
        r"^(implementation)\W",
        TokenType.Implementation,
        1,
        0
    ),
    TokenMatcher(r"^(interface)\W", TokenType.Interface, 1),

    TokenMatcher(r"^(const)\W", TokenType.Const, 1),
    TokenMatcher(r"^(var)\W", TokenType.Var, 1),
    TokenMatcher(r"^(if)\W", TokenType.If, 1),
    TokenMatcher(r"^(else)\W", TokenType.Else, 1),
    TokenMatcher(r"^(match)\W", TokenType.Match, 1),
    TokenMatcher(r"^(switch)\W", TokenType.Switch, 1),
    TokenMatcher(r"^(case)\W", TokenType.Case, 1),
    TokenMatcher(r"^(default)\W", TokenType.Default, 1),
    TokenMatcher(r"^(for)\W", TokenType.For, 1),
    TokenMatcher(r"^(loop)\W", TokenType.Loop, 1),
    TokenMatcher(r"^(while)\W", TokenType.While, 1),
    TokenMatcher(r"^(break)\W", TokenType.Break, 1),
    TokenMatcher(r"^(continue)\W", TokenType.Continue, 1),
    TokenMatcher(r"^(return)\W", TokenType.Return, 1),

    TokenMatcher(r"^[\@]*\w+", TokenType.Value)
]


class Lexer:

    class State:

        __slots__ = ('index', 'line', 'column', 'should_skip_funcs')

        def __init__(self, index, line, column, should_skip_funcs):
            self.index = index
            self.line = line
            self.column = column
            self.should_skip_funcs = should_skip_funcs

    def __init__(self, data_source):
        self.data_source = data_source
        self.location = Location(self.data_source)
        self.should_skip_funcs = [
            lambda token: token.categories.intersection({
                TokenCategory.Blank,
                TokenCategory.Comment
            })
        ]
        self._states = []

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self.lex()
        except errors.EOF:
            raise StopIteration()

    def _should_skip(self, token):
        return any([f(token) for f in self.should_skip_funcs])

    def _lex_token(self):
        try:
            data = self.data_source.at(self.location)
        except IndexError:
            raise errors.EOF() from None

        for matcher in TOKEN_MATCHERS:
            match = matcher.regex.match(data)
            if not match:
                continue
            value = match.group(matcher.group_index)
            token = Token(
                self.location.copy(),
                matcher.token_type,
                matcher.token_type.has_value and value or None
            )
            token_length = len(value) + matcher.extra_skip
            self.location.index += token_length
            if token.token_type in (TokenType.LineBreak, TokenType.Comment):
                self.location.line += 1
                self.location.column = 1
            else:
                self.location.column += token_length
            break
        else:
            token = Token(self.location.copy(), TokenType.Unknown, data[0])
            self.location.index += 1
            self.location.column += 1

        return token

    def get_state(self):
        return Lexer.State(
            self.location.index,
            self.location.line,
            self.location.column,
            self.should_skip_funcs
        )

    def set_state(self, state):
        self.location.index = state.index
        self.location.line = state.line
        self.location.column = state.column
        # pylint: disable=unnecessary-comprehension
        self.should_skip_funcs = [func for func in state.should_skip_funcs]

    def lex(self):
        token = self._lex_token()
        while self._should_skip(token):
            token = self._lex_token()
        debug(f'Returning {token}')
        return token

    def next_matches(self, token_types=None, token_categories=None):
        state = self.get_state()
        matches = self.lex().matches(token_types, token_categories)
        self.set_state(state)
        return matches

    def get_next_if_matches(self, token_types=None, token_categories=None):
        state = self.get_state()
        token = self.lex()
        if not token.matches(token_types, token_categories):
            self.set_state(state)
            return None
        return token

    def get_next_if_not_matches(self, token_types=None, token_categories=None):
        state = self.get_state()
        token = self.lex()
        if token.matches(token_types, token_categories):
            self.set_state(state)
            return None
        return token

    def skip_next_if_matches(self, token_types=None, token_categories=None):
        state = self.get_state()
        if not self.lex().matches(token_types, token_categories):
            self.set_state(state)
            return False
        return True

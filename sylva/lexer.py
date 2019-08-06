import re

from collections import namedtuple

from . import errors
from .location import Location
from .token import Token, TokenCategory, TokenType


TokenMatcher = namedtuple(
    'TokenMatcher',
    ('regex', 'token_type', 'group_index', 'extra_skip'),
    defaults=(0, 0)
)


TOKEN_MATCHERS = [
    TokenMatcher(re.compile(r"^#(.*)(\r\n|\r|\n)"), TokenType.Comment),
    TokenMatcher(re.compile(r"^( |\t)+"), TokenType.Space),
    TokenMatcher(re.compile(r"^(\r\n|\r|\n)"), TokenType.LineBreak),
    TokenMatcher(
        re.compile(r"^\d[\d_]*\.\d[\d_]*[Ee][+-]*\d[\d_]*"),
        TokenType.Decimal
    ),
    TokenMatcher(
        re.compile(r"^\.\d[\d_]*[Ee][+-]*\d[\d_]*"), TokenType.Decimal
    ),
    TokenMatcher(
        re.compile(r"^\d[\d_]*[Ee][+-]*\d[\d_]*"),
        TokenType.Decimal
    ),
    TokenMatcher(re.compile(r"^\d[\d_]*\.\d[\d_]*"), TokenType.Decimal),
    TokenMatcher(re.compile(r"^\.\d[\d_]*"), TokenType.Decimal),
    TokenMatcher(re.compile(r"^Infinity"), TokenType.Decimal),
    TokenMatcher(re.compile(r"^NaN"), TokenType.Decimal),
    TokenMatcher(
        re.compile(r"^(0[Bb][01]+)s"), TokenType.SignedBinInteger, 1, 1
    ),
    TokenMatcher(
        re.compile(r"^(0[Bb][01]+)u"), TokenType.UnsignedBinInteger, 1, 1
    ),
    TokenMatcher(re.compile(r"^0[Bb][01]+"), TokenType.Decimal),
    TokenMatcher(
        re.compile(r"^(0[Oo][01234567]+)s"), TokenType.SignedOctInteger, 1, 1
    ),
    TokenMatcher(
        re.compile(r"^(0[Oo][01234567]+)u"), TokenType.UnsignedOctInteger, 1, 1
    ),
    TokenMatcher(re.compile(r"^0[Oo][01234567]+"), TokenType.Decimal),
    TokenMatcher(
        re.compile(r"^(0[Xx][0123456789aAbBcCdDeEfF]+)s"),
        TokenType.SignedHexInteger,
        1,
        1
    ),
    TokenMatcher(
        re.compile(r"^(0[Xx][0123456789aAbBcCdDeEfF]+)u"),
        TokenType.UnsignedHexInteger,
        1,
        1
    ),
    TokenMatcher(
        re.compile(r"^0[Xx][0123456789aAbBcCdDeEfF]+"), TokenType.Decimal
    ),
    TokenMatcher(re.compile(r"^(\d+)s"), TokenType.SignedDecInteger, 1, 1),
    TokenMatcher(re.compile(r"^(\d+)u"), TokenType.UnsignedDecInteger, 1, 1),
    TokenMatcher(re.compile(r"^\d+"), TokenType.Decimal),
    TokenMatcher(re.compile(r'"(.*?)"'), TokenType.String, 1, 2),
    TokenMatcher(re.compile(r"^'(.*?)'"), TokenType.Rune, 1, 2),
    TokenMatcher(re.compile(r"^(true)\W"), TokenType.Boolean, 1),
    TokenMatcher(re.compile(r"^(false)\W"), TokenType.Boolean, 1),
    TokenMatcher(re.compile(r"^\("), TokenType.OpenParen),
    TokenMatcher(re.compile(r"^\)"), TokenType.CloseParen),
    TokenMatcher(re.compile(r"^\["), TokenType.OpenBracket),
    TokenMatcher(re.compile(r"^]"), TokenType.CloseBracket),
    TokenMatcher(re.compile(r"^{"), TokenType.OpenBrace),
    TokenMatcher(re.compile(r"^}"), TokenType.CloseBrace),
    TokenMatcher(re.compile(r"^,"), TokenType.Comma),
    TokenMatcher(re.compile(r"^`"), TokenType.Tilde),
    TokenMatcher(re.compile(r"^\|\|"), TokenType.BooleanOr),
    TokenMatcher(re.compile(r"^\|="), TokenType.BinaryOrAssign),
    TokenMatcher(re.compile(r"^\|"), TokenType.BinaryOr),
    TokenMatcher(re.compile(r"^&&"), TokenType.BooleanAnd),
    TokenMatcher(re.compile(r"^&="), TokenType.BinaryAndAssign),
    TokenMatcher(re.compile(r"^&"), TokenType.BinaryAnd),
    TokenMatcher(re.compile(r"^==="), TokenType.IdentityEqual),
    TokenMatcher(re.compile(r"^=="), TokenType.Equal),
    TokenMatcher(re.compile(r"^="), TokenType.Assign),
    TokenMatcher(re.compile(r"^!=="), TokenType.IdentityNotEqual),
    TokenMatcher(re.compile(r"^!="), TokenType.NotEqual),
    TokenMatcher(re.compile(r"^!"), TokenType.BooleanNot),
    TokenMatcher(re.compile(r"^\^="), TokenType.BinaryXorAssign),
    TokenMatcher(re.compile(r"^\^"), TokenType.BinaryXor),
    TokenMatcher(re.compile(r"^>>>="), TokenType.UnsignedRightShiftAssign),
    TokenMatcher(re.compile(r"^>>>"), TokenType.UnsignedRightShift),
    TokenMatcher(re.compile(r"^>>="), TokenType.RightShiftAssign),
    TokenMatcher(re.compile(r"^>>"), TokenType.RightShift),
    TokenMatcher(re.compile(r"^>="), TokenType.GreaterThanOrEqual),
    TokenMatcher(re.compile(r"^>"), TokenType.GreaterThan),
    TokenMatcher(re.compile(r"^<<="), TokenType.LeftShiftAssign),
    TokenMatcher(re.compile(r"^<<"), TokenType.LeftShift),
    TokenMatcher(re.compile(r"^<="), TokenType.LessThanOrEqual),
    TokenMatcher(re.compile(r"^<"), TokenType.LessThan),
    TokenMatcher(re.compile(r"^\+\+"), TokenType.Increment),
    TokenMatcher(re.compile(r"^\+="), TokenType.PlusAssign),
    TokenMatcher(re.compile(r"^\+"), TokenType.Plus),
    TokenMatcher(re.compile(r"^--"), TokenType.Decrement),
    TokenMatcher(re.compile(r"^-="), TokenType.MinusAssign),
    TokenMatcher(re.compile(r"^-"), TokenType.Minus),
    TokenMatcher(re.compile(r"^\*\*="), TokenType.ExponentAssign),
    TokenMatcher(re.compile(r"^\*\*"), TokenType.Exponent),
    TokenMatcher(re.compile(r"^\*="), TokenType.MultiplyAssign),
    TokenMatcher(re.compile(r"^\*"), TokenType.Multiply),
    TokenMatcher(re.compile(r"^//="), TokenType.IntegerDivideAssign),
    TokenMatcher(re.compile(r"^//"), TokenType.IntegerDivide),
    TokenMatcher(re.compile(r"^/="), TokenType.DivideAssign),
    TokenMatcher(re.compile(r"^/"), TokenType.Divide),
    TokenMatcher(re.compile(r"^%="), TokenType.RemainderAssign),
    TokenMatcher(re.compile(r"^%"), TokenType.Remainder),
    TokenMatcher(re.compile(r"^~"), TokenType.BinaryNot),
    TokenMatcher(re.compile(r"^\."), TokenType.AttributeLookup),
    TokenMatcher(re.compile(r"^::"), TokenType.ReflectionLookup),
    TokenMatcher(re.compile(r"^:"), TokenType.Colon),
    TokenMatcher(re.compile(r"^(fn)\W"), TokenType.Fn, 1),
    TokenMatcher(re.compile(r"^(fntype)\W"), TokenType.FnType, 1),
    TokenMatcher(re.compile(r"^(struct)\W"), TokenType.Struct, 1),
    TokenMatcher(re.compile(r"^(array)\W"), TokenType.Array, 1),
    TokenMatcher(re.compile(r"^(extern)\W"), TokenType.Extern, 1),
    TokenMatcher(re.compile(r"^(alias)\W"), TokenType.Alias, 1),
    TokenMatcher(re.compile(r"^(module)\W"), TokenType.Module, 1),
    TokenMatcher(
        re.compile(r"^(implementation)\W"),
        TokenType.Implementation,
        1,
        0
    ),
    TokenMatcher(re.compile(r"^(interface)\W"), TokenType.Interface, 1),
    TokenMatcher(re.compile(r"^[\@]*\w+"), TokenType.Value)
]


class Lexer:

    State = namedtuple('State', ('index', 'line', 'column', 'funcs'))

    def __init__(self, location):
        self.location = location
        self.data_source = location.data_source
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
            raise errors.EOF()

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
        self.should_skip_funcs = [func for func in self.should_skip_funcs]

    def lex(self):
        token = self._lex_token()
        while self._should_skip(token):
            token = self._lex_token()
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
        if not token.matches(token_types, token_categories):
            self.set_state(state)
            return None
        return token

    def skip_next_if_matches(self, token_types=None, token_categories=None):
        state = self.get_state()
        if not self.lex().matches(token_types, token_categories):
            self.set_state(state)
            return False
        return True

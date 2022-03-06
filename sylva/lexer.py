import re

from contextlib import contextmanager

from . import errors
from . import token_type as TokenType

from .location import Location
from .token import Token
from .token_category import TokenCategory


class TokenMatcher:

    __slots__ = ('regex', 'token_type', 'extra_skip')

    def __init__(self, rstr, token_type, extra_skip=0):
        self.regex = re.compile(rstr)
        self.token_type = token_type
        self.extra_skip = extra_skip

    def update_token_kwargs(self, token):
        pass


class BlankTokenMatcher(TokenMatcher):

    __slots__ = ('regex', 'token_type', 'extra_skip')

    def __init__(self, rstr, token_type):
        super().__init__(rstr, token_type, extra_skip=0)


class SymbolTokenMatcher(TokenMatcher):

    __slots__ = ('regex', 'token_type', 'extra_skip')

    def __init__(self, rstr, token_type):
        super().__init__(r'(' + rstr + r')', token_type, extra_skip=0)


class DelimitedTokenMatcher(TokenMatcher):

    __slots__ = ('regex', 'token_type', 'extra_skip')

    def __init__(self, rstr, token_type):
        super().__init__(r'(' + rstr + r')(?=$|\W)', token_type, extra_skip=0)


class NumericTokenMatcher(TokenMatcher):

    __slots__ = ('regex', 'token_type', 'extra_skip')

    def __init__(self, rstr, token_type):
        super().__init__(rstr + r'(?=$|\W)', token_type, extra_skip=0)


class IntegerTokenMatcher(TokenMatcher):

    __slots__ = ('regex', 'token_type', 'extra_skip', 'base')

    def __init__(self, rstr, token_type, base):
        super().__init__(rstr + r'(?=$|\W)', token_type, extra_skip=1)
        self.base = base

    def update_token_kwargs(self, token):
        token.kwargs['base'] = self.base


class QuotedTokenMatcher(TokenMatcher):

    __slots__ = ('regex', 'token_type', 'extra_skip')

    def __init__(self, rstr, token_type):
        super().__init__(rstr, token_type, extra_skip=2)


_BIN_VALUE = r'(?P<value>-??0[Bb][01]+?)'
_OCT_VALUE = r'(?P<value>-??0[Oo][01234567]+?)'
_DEC_VALUE = r'(?P<value>-??\d+?)'
_HEX_VALUE = r'(?P<value>-??0[Xx][0123456789aAbBcCdDeEfF]+?)'
_ALL_FLT_VALUE = r'(?P<value>-??\d+?\.\d+?([Ee]-??\d+?)??)'
_INT_FLT_VALUE = r'(?P<value>-??\d+?\.([Ee]-??\d+?)??)'
_DEC_FLT_VALUE = r'(?P<value>-??\.??\d+?([Ee]-??\d+?)??)'
_EXP_FLT_VALUE = r'(?P<value>-??\d+?[Ee]-??\d+?)'
_NAN_FLT_VALUE = r'(?P<value>NaN|nan|NAN)'
_INF_FLT_VALUE = r'(?P<value>-??Inf|inf|INF)'
_INT_SIGNEDNESS = r'(?P<signedness>i|u)'
_NUMBER_SIZES = r'(?P<size>8|16|32|64|128)??'
_INT_OVERFLOWS = r'(?P<overflow>w|c)??'
_ROUNDS = r'(?P<round>rn|ru|rd|rz|ra)??'

_INT_SUFFIX = _INT_SIGNEDNESS + _NUMBER_SIZES + _INT_OVERFLOWS
_FLT_SUFFIX = r'f' + _NUMBER_SIZES + _ROUNDS
_DEC_SUFFIX = _ROUNDS


TOKEN_MATCHERS = [
    TokenMatcher(r'#(?P<value>.*)(\r\n|\r|\n)', TokenType.Comment),
    BlankTokenMatcher(r'( |\t)+', TokenType.Space),
    BlankTokenMatcher(r'(\r\n|\r|\n)', TokenType.LineBreak),

    NumericTokenMatcher(_ALL_FLT_VALUE + _FLT_SUFFIX, TokenType.Float),
    NumericTokenMatcher(_INT_FLT_VALUE + _FLT_SUFFIX, TokenType.Float),
    NumericTokenMatcher(_DEC_FLT_VALUE + _FLT_SUFFIX, TokenType.Float),
    NumericTokenMatcher(_EXP_FLT_VALUE + _FLT_SUFFIX, TokenType.Float),
    NumericTokenMatcher(_NAN_FLT_VALUE + _FLT_SUFFIX, TokenType.Float),
    NumericTokenMatcher(_INF_FLT_VALUE + _FLT_SUFFIX, TokenType.Float),

    IntegerTokenMatcher(_BIN_VALUE + _INT_SUFFIX, TokenType.Integer, base=2),
    IntegerTokenMatcher(_OCT_VALUE + _INT_SUFFIX, TokenType.Integer, base=8),
    IntegerTokenMatcher(_DEC_VALUE + _INT_SUFFIX, TokenType.Integer, base=10),
    IntegerTokenMatcher(_HEX_VALUE + _INT_SUFFIX, TokenType.Integer, base=16),

    NumericTokenMatcher(_ALL_FLT_VALUE + _DEC_SUFFIX, TokenType.Decimal),
    NumericTokenMatcher(_INT_FLT_VALUE + _DEC_SUFFIX, TokenType.Decimal),
    NumericTokenMatcher(_DEC_FLT_VALUE + _DEC_SUFFIX, TokenType.Decimal),
    NumericTokenMatcher(_EXP_FLT_VALUE + _DEC_SUFFIX, TokenType.Decimal),
    NumericTokenMatcher(_NAN_FLT_VALUE + _DEC_SUFFIX, TokenType.Decimal),
    NumericTokenMatcher(_INF_FLT_VALUE + _DEC_SUFFIX, TokenType.Decimal),

    IntegerTokenMatcher(_BIN_VALUE + _DEC_SUFFIX, TokenType.Decimal, base=2),
    IntegerTokenMatcher(_OCT_VALUE + _DEC_SUFFIX, TokenType.Decimal, base=8),
    IntegerTokenMatcher(_DEC_VALUE + _DEC_SUFFIX, TokenType.Decimal, base=10),
    IntegerTokenMatcher(_HEX_VALUE + _DEC_SUFFIX, TokenType.Decimal, base=16),

    QuotedTokenMatcher(r'"(?P<value>.*?)"', TokenType.String),
    QuotedTokenMatcher(r"'(?P<value>.*?)'", TokenType.Rune),
    DelimitedTokenMatcher(r'(?P<value>true)', TokenType.Boolean),
    DelimitedTokenMatcher(r'(?P<value>false)', TokenType.Boolean),
    SymbolTokenMatcher(r'\(', TokenType.OpenParen),
    SymbolTokenMatcher(r'\)', TokenType.CloseParen),
    SymbolTokenMatcher(r'\[', TokenType.OpenBracket),
    SymbolTokenMatcher(r']', TokenType.CloseBracket),
    SymbolTokenMatcher(r'{', TokenType.OpenBrace),
    SymbolTokenMatcher(r'}', TokenType.CloseBrace),
    SymbolTokenMatcher(r',', TokenType.Comma),
    SymbolTokenMatcher(r';', TokenType.Semicolon),
    SymbolTokenMatcher(r'`', TokenType.Tilde),
    SymbolTokenMatcher(r'\|\|', TokenType.DoublePipe),
    SymbolTokenMatcher(r'\|=', TokenType.PipeEqual),
    SymbolTokenMatcher(r'\|', TokenType.Pipe),
    SymbolTokenMatcher(r'&&', TokenType.Ampersand),
    SymbolTokenMatcher(r'&=', TokenType.AmpersandEqual),
    SymbolTokenMatcher(r'&', TokenType.Ampersand),
    SymbolTokenMatcher(r'==', TokenType.DoubleEqual),
    SymbolTokenMatcher(r'=', TokenType.Equal),
    SymbolTokenMatcher(r'!=', TokenType.BangEqual),
    SymbolTokenMatcher(r'!', TokenType.Bang),
    SymbolTokenMatcher(r'\^=', TokenType.CaretEqual),
    SymbolTokenMatcher(r'\^', TokenType.Caret),
    SymbolTokenMatcher(r'>>>=', TokenType.TripleCloseAngleEqual),
    SymbolTokenMatcher(r'>>>', TokenType.TripleCloseAngle),
    SymbolTokenMatcher(r'>>=', TokenType.DoubleCloseAngleEqual),
    SymbolTokenMatcher(r'>>', TokenType.DoubleCloseAngle),
    SymbolTokenMatcher(r'>=', TokenType.CloseAngleEqual),
    SymbolTokenMatcher(r'>', TokenType.CloseAngle),
    SymbolTokenMatcher(r'<<=', TokenType.DoubleOpenAngleEqual),
    SymbolTokenMatcher(r'<<', TokenType.DoubleOpenAngle),
    SymbolTokenMatcher(r'<=', TokenType.OpenAngleEqual),
    SymbolTokenMatcher(r'<', TokenType.OpenAngle),
    SymbolTokenMatcher(r'\+\+', TokenType.DoublePlus),
    SymbolTokenMatcher(r'\+=', TokenType.PlusEqual),
    SymbolTokenMatcher(r'\+', TokenType.Plus),
    SymbolTokenMatcher(r'--', TokenType.DoubleMinus),
    SymbolTokenMatcher(r'-=', TokenType.MinusEqual),
    SymbolTokenMatcher(r'-', TokenType.Minus),
    SymbolTokenMatcher(r'\*\*=', TokenType.DoubleStarEqual),
    SymbolTokenMatcher(r'\*\*', TokenType.DoubleStar),
    SymbolTokenMatcher(r'\*=', TokenType.StarEqual),
    SymbolTokenMatcher(r'\*', TokenType.Star),
    SymbolTokenMatcher(r'/=', TokenType.SlashEqual),
    SymbolTokenMatcher(r'/', TokenType.Slash),
    SymbolTokenMatcher(r'%=', TokenType.PercentEqual),
    SymbolTokenMatcher(r'%', TokenType.Percent),
    SymbolTokenMatcher(r'~', TokenType.Tilde),
    SymbolTokenMatcher(r'\.\.\.', TokenType.Ellipsis),
    SymbolTokenMatcher(r'\.', TokenType.Dot),
    SymbolTokenMatcher(r'::', TokenType.DoubleColon),
    SymbolTokenMatcher(r':', TokenType.Colon),

    DelimitedTokenMatcher(r'mod', TokenType.Module),
    DelimitedTokenMatcher(r'req', TokenType.Requirement),
    DelimitedTokenMatcher(r'fn', TokenType.Fn),
    DelimitedTokenMatcher(r'fntype', TokenType.FnType),
    DelimitedTokenMatcher(r'struct', TokenType.Struct),
    DelimitedTokenMatcher(r'variant', TokenType.Variant),
    DelimitedTokenMatcher(r'enum', TokenType.Enum),
    DelimitedTokenMatcher(r'range', TokenType.Range),

    DelimitedTokenMatcher(r'cfn', TokenType.CFn),
    DelimitedTokenMatcher(r'cfntype', TokenType.CFnType),
    DelimitedTokenMatcher(r'cblockfntype', TokenType.CFnType),
    DelimitedTokenMatcher(r'cstruct', TokenType.CStruct),
    DelimitedTokenMatcher(r'cunion', TokenType.CUnion),

    DelimitedTokenMatcher(r'alias', TokenType.Alias),
    DelimitedTokenMatcher(r'impl', TokenType.Implementation),
    DelimitedTokenMatcher(r'iface', TokenType.Interface),

    DelimitedTokenMatcher(r'const', TokenType.Const),
    DelimitedTokenMatcher(r'var', TokenType.Var),
    DelimitedTokenMatcher(r'if', TokenType.If),
    DelimitedTokenMatcher(r'else', TokenType.Else),
    DelimitedTokenMatcher(r'match', TokenType.Match),
    DelimitedTokenMatcher(r'switch', TokenType.Switch),
    DelimitedTokenMatcher(r'case', TokenType.Case),
    DelimitedTokenMatcher(r'default', TokenType.Default),
    DelimitedTokenMatcher(r'for', TokenType.For),
    DelimitedTokenMatcher(r'loop', TokenType.Loop),
    DelimitedTokenMatcher(r'while', TokenType.While),
    DelimitedTokenMatcher(r'break', TokenType.Break),
    DelimitedTokenMatcher(r'continue', TokenType.Continue),
    DelimitedTokenMatcher(r'return', TokenType.Return),

    TokenMatcher(r'(?P<value>[\@]*\w+)', TokenType.Value)
]


class Lexer:

    class State:

        __slots__ = (
            'index', 'line', 'column', 'should_skip_funcs', 'prev', 'buffer'
        )

        def __init__(self, index, line, column, should_skip_funcs, prev,
                     buffer):
            self.index = index
            self.line = line
            self.column = column
            self.should_skip_funcs = should_skip_funcs
            self.prev = prev
            self.buffer = buffer

    def __init__(self, data_source):
        self.data_source = data_source
        self.location = Location(self.data_source)
        self.should_skip_funcs = [
            lambda token: token.categories.intersection({
                TokenCategory.Blank,
                TokenCategory.Comment
            })
        ]
        self.prev = None
        self.buffer = []

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self.lex()
        except errors.EOF:
            raise StopIteration() from None

    def __repr__(self):
        return 'Lexer(%r)' % (self.location)

    def _should_skip(self, token):
        return any(f(token) for f in self.should_skip_funcs)

    def _lex_token(self):
        if self.buffer:
            return self.buffer.pop(0)

        try:
            data = self.data_source.at(self.location)
        except IndexError:
            raise errors.EOF() from None

        for matcher in TOKEN_MATCHERS:
            match = matcher.regex.match(data)
            if not match:
                continue
            md = match.groupdict()
            token = Token(self.location.copy(), matcher.token_type, **md)
            matcher.update_token_kwargs(token)
            token_length = match.end()
            self.location.index += token_length
            if token.matches_types({TokenType.LineBreak, TokenType.Comment}):
                self.location.line += 1
                self.location.column = 1
            else:
                self.location.column += token_length
            break
        else:
            token = Token(
                self.location.copy(),
                TokenType.Unknown,
                value=data[0]
            )
            self.location.index += 1
            self.location.column += 1

        if token.matches_category(TokenCategory.SyntaxSugar):
            self.buffer.expand(token.desugar(self.prev))
            return self.buffer.pop(0)

        return token

    def get_state(self):
        return Lexer.State(
            self.location.index,
            self.location.line,
            self.location.column,
            self.should_skip_funcs,
            self.buffer,
            self.prev
        )

    def set_state(self, state):
        self.location.index = state.index
        self.location.line = state.line
        self.location.column = state.column
        self.should_skip_funcs = state.should_skip_funcs
        self.buffer = state.buffer
        self.prev = state.prev

    @contextmanager
    def save_state(self):
        state = self.get_state()
        try:
            yield state
        finally:
            self.set_state(state)

    def lex(self):
        token = self._lex_token()
        while self._should_skip(token):
            token = self._lex_token()
        return token

    def next_matches(self, token_types=None, token_categories=None):
        with self.save_state():
            return self.lex().matches(token_types, token_categories)

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

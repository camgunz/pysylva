from . import errors

from .token_category import TokenCategory


class Token:

    __slots__ = ('location', 'token_type', 'value', 'kwargs')

    def __init__(self, location, token_type, **kwargs):
        self.location = location
        self.token_type = token_type
        self.value = kwargs.pop('value', None)
        self.kwargs = kwargs

    @property
    def categories(self):
        return self.token_type.categories

    @property
    def is_syntax_sugar(self):
        return TokenCategory.SyntaxSugar in self.categories

    @property
    def operator(self):
        return self.token_type.operator

    @property
    def syntax_sugar(self):
        return self.token_type.syntax_sugar

    def __getitem__(self, item):
        return self.kwargs[item]

    def get(self, item, default=None):
        return self.kwargs.get(item, default)

    def __repr__(self):
        if self.value:
            return 'Token(%r, %r, %r, %r)' % (
                self.location, self.token_type, self.value, self.kwargs
            )
        return 'Token(%r, %r)' % (self.location, self.token_type)

    def __str__(self):
        if self.value and self.kwargs:
            return f'{self.token_type.name}Token({self.value}, {self.kwargs})'
        if self.value:
            return f'{self.token_type.name}Token({self.value})'
        return f'{self.token_type.name}Token'

    def matches(self, token_types=None, token_categories=None):
        return (
            (token_types and self.token_type in token_types) or
            (token_categories and
                self.categories.intersection(token_categories))
        )

    def matches_types(self, token_types):
        return self.matches(token_types=token_types)

    def matches_type(self, token_type):
        return self.matches_types([token_type])

    def matches_categories(self, token_categories):
        return self.matches(token_categories=token_categories)

    def matches_category(self, token_category):
        return self.matches_categories([token_category])

    def desugar(self, prev):
        tokens = []

        if not self.is_syntax_sugar:
            return tokens

        for sub_token in self.syntax_sugar:
            if sub_token == '<prev>':
                if prev is None:
                    raise errors.InvalidOperatorExpansion(
                        self.location,
                        'No previous token'
                    )
                if not prev.matches_category(TokenCategory.Number):
                    raise errors.InvalidOperatorExpansion(
                        self.location,
                        'Preceding token is not numeric'
                    )
                tokens.append(prev)
            elif sub_token == '<one>':
                if prev is None:
                    raise errors.InvalidOperatorExpansion(
                        self.location,
                        'No previous token'
                    )
                if not prev.matches_category(TokenCategory.Number):
                    raise errors.InvalidOperatorExpansion(
                        self.location,
                        'Preceding token is not numeric'
                    )
                tokens.append(Token(
                    prev.location.copy(),
                    prev.token_type,
                    **{'value': '1', **prev.kwargs}
                ))
            else:
                tokens.append(sub_token)

        return tokens

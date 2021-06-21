from .utils import strlist


class SylvaError(Exception):

    def pformat(self):
        return f'[Error: {self}]'


class EOF(SylvaError):
    pass


class LocationError(SylvaError):

    def __init__(self, location, message):
        self.location = location
        super().__init__(message)

    def pformat(self):
        return (
            '\n'
            f'[Error: {self.location.shorthand}] {self}'
            '\n'
            f'{self.location.pformat()}'
        )


class UnexpectedTokenType(LocationError):

    def __init__(self, token, expected_token_types):
        super().__init__(token.location, (
            f'Unexpected token type {token.token_type} ({token}); '
            f'expected: {strlist(expected_token_types)}'
        ))


class UnexpectedTokenCategory(LocationError):

    def __init__(self, token, expected_token_categories):
        super().__init__(token.location, (
            f'Unexpected token {token}; '
            f'expected: {strlist(expected_token_categories)}'
        ))


class UnexpectedToken(LocationError):

    def __init__(self, token, expected_token_types, expected_token_categories):
        super().__init__(token.location, (
            f'Unexpected token {token}; '
            f'expected: {strlist(expected_token_types)} or '
            f' {strlist(expected_token_categories)}'
        ))

class LiteralParseFailure(LocationError):

    def __init__(self, literal):
        super().__init__(literal.location, (
            f'Unable to parse {literal.raw_value} as {type(literal).__name__}'
        ))


class InvalidExpression(LocationError):

    def __init__(self, location):
        super().__init__(location, 'Invalid expression')


class NoOperatorForToken(LocationError):

    def __init__(self, token):
        super().__init__(
            token.location,
            f'No operator for {token.token_type.name}'
        )


class MultipleOperatorsForToken(LocationError):

    def __init__(self, token, operators):
        super().__init__(
            token.location,
            f'Multiple operators for {token.token_type.name}: '
            f'{strlist(operators)}'
        )


class UndefinedSymbol(LocationError):

    def __init__(self, location, name):
        super().__init__(location, f'Undefined symbol {name}')


class DuplicateDefinition(LocationError):

    def __init__(self, existing_location, location):
        super().__init__(
            location,
            f'Variable already defined: [{existing_location.shorthand}]'
        )


class NoSuchModule(SylvaError):

    def __init__(self, module_name):
        super().__init__(f'No such module {module_name}')


class MutatingBuiltins(SylvaError):

    def __init__(self, builtin_module_statements):
        super().__init__(
            'Cannot modify builtins:\n' + '\n'.join([
                f'\t{module_name}: {location.pformat()}'
                for location, module_name in builtin_module_statements
            ])
        )


class RedundantAlias(LocationError):

    def __init__(self, location, name):
        super().__init__(location, f'Alias for {name} is redundant')


class DuplicateAlias(LocationError):

    def __init__(self, location, name):
        super().__init__(location, f'Alias {name} already defined')

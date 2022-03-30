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
            f'{self.location.pformat()}'
            '\n'
            '\n'
            f'[Error: {self.location.shorthand}] {self}'
            '\n'
        )


class UnexpectedTokenType(LocationError):

    def __init__(self, token, expected_token_types):
        super().__init__(
            token.location,
            (
                f'Unexpected token type {token.token_type} ({token}); '
                f'expected: {strlist(expected_token_types)}'
            )
        )


class UnexpectedTokenCategory(LocationError):

    def __init__(self, token, expected_token_categories):
        super().__init__(
            token.location,
            (
                f'Unexpected token {token}; '
                f'expected: {strlist(expected_token_categories)}'
            )
        )


class UnexpectedToken(LocationError):

    def __init__(self, token, expected_token_types, expected_token_categories):
        super().__init__(
            token.location,
            (
                f'Unexpected token {token}; '
                f'expected: {strlist(expected_token_types)} or '
                f' {strlist(expected_token_categories)}'
            )
        )


class SignedSizeError(LocationError):

    def __init__(self, location):
        super().__init__(location, 'Size must be an unsigned integer')


class LiteralParseFailure(LocationError):

    def __init__(self, literal_type, token, message=None):
        name = literal_type.__name__
        message = f': {message}' if message else ''
        super().__init__(
            token.location,
            f'Unable to parse {token.value} as {name}{message}'
        )


class InvalidOperatorExpansion(LocationError):

    def __init__(self, location, message):
        super().__init__(location, f'Invalid operator expansion: {message}')


class InvalidExpressionType(LocationError):

    def __init__(self, location, expected, actual):
        super().__init__(
            location,
            f'Invalid expression type. Expected {expected}; got {actual}'
        )


class InvalidExpression(LocationError):

    def __init__(self, location):
        super().__init__(location, 'Invalid expression')


class EmptyExpression(LocationError):

    def __init__(self, location):
        super().__init__(location, 'Empty expression')


class InvalidOperatorArity(LocationError):

    def __init__(self, location, expected_arity):
        super().__init__(
            location, f'Expected {expected_arity.name.lower()} operator'
        )


class UndefinedSymbol(LocationError):

    def __init__(self, location, name):
        super().__init__(location, f'Undefined symbol {name}')


class DuplicateDefinition(LocationError):

    def __init__(self, location, existing_location):
        super().__init__(
            location,
            f'Variable already defined: [{existing_location.shorthand}]'
        )


class NoSuchModule(LocationError):

    def __init__(self, location, module_name):
        super().__init__(location, f'No such module {module_name}')


class MutatingBuiltins(SylvaError):

    def __init__(self, builtin_module_statements):
        super().__init__(
            'Cannot modify builtins:\n' + '\n'.join([
                f'\t{module_name}: {location.pformat()}' for location,
                module_name in builtin_module_statements
            ])
        )


class RedundantAlias(LocationError):

    def __init__(self, location, name):
        super().__init__(location, f'Alias for {name} is redundant')


class DuplicateAlias(LocationError):

    def __init__(self, location, existing_location, name):
        super().__init__(location, f'Alias {name} already defined')


class CircularDependency(SylvaError):

    def __init__(self, module, seen):
        super().__init__(f'Circular dependency: {module} cannot be in {seen}')

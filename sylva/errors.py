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

    def __init__(self, location, token, expected_tokens):
        if token == '"':
            token = f"'{token}'"
        else:
            token = f'"{token}"'
        super().__init__(
            location,
            (
                f'Unexpected token {token}; '
                f'expected: {strlist(expected_tokens)}'
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

    def __init__(self, location, expected):
        super().__init__(
            location, f'Invalid expression type; expected {expected}'
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


class NoSuchAttribute(LocationError):

    def __init__(self, location, name):
        super().__init__(location, f'No such field {name}')


class DuplicateDefinition(LocationError):

    def __init__(self, name, location, existing_location):
        super().__init__(
            location,
            f'"{name}" already defined: [{existing_location.shorthand}]'
        )


class RedefinedBuiltIn(LocationError):

    def __init__(self, definition):
        super().__init__(
            definition.location,
            f'Cannot redefine builtin "{definition.name}"'
        )


class DefinitionViolation(LocationError):

    def __init__(self, location, name):
        super().__init__(
            location, f'Cannot define "{name}" in external module'
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
        super().__init__(
            location,
            f'Alias {name} already defined at {existing_location.shorthand}'
        )


class CircularDependency(SylvaError):

    def __init__(self, module, seen):
        super().__init__(f'Circular dependency: {module} cannot be in {seen}')


class EmptyVariant(LocationError):

    def __init__(self, variant):
        super().__init__(variant.location, 'Variant has no fields')


class DuplicateVariantFields(LocationError):

    def __init__(self, name, variant, dupes):
        super().__init__(
            variant.location, f'Duplicate fields in {name}: {strlist(dupes)}'
        )


class DuplicateEnumFields(LocationError):

    def __init__(self, name, enum, dupes):
        super().__init__(
            enum.location, f'Duplicate fields in {name}: {strlist(dupes)}'
        )


class EmptyEnum(LocationError):

    def __init__(self, location):
        super().__init__(location, 'Enum has no fields')


class MismatchedEnumMemberType(LocationError):

    def __init__(self, type, member):
        super().__init__(
            member.location,
            f'Mismatched enum type: expected {type}; got {member.type}'
        )


class MismatchedRangeTypes(LocationError):

    def __init__(self, location, min_type, max_type):
        super().__init__(
            location, f'Mismatched range types: {min_type} {max_type}'
        )


class MismatchedElementType(LocationError):

    def __init__(self, type, element):
        super().__init__(
            element.location,
            f'Mismatched element type: expected {type}; got {element.type}'
        )


class MissingTypeParam(LocationError):

    def __init__(self, location, type_param):
        super().__init__(location, f'Missing type parameter {type_param}')


class DuplicateFields(LocationError):

    def __init__(self, obj, dupes):
        super().__init__(obj.location, f'Duplicate fields: {strlist(dupes)}')


class DuplicateParameters(LocationError):

    def __init__(self, obj, dupes):
        super().__init__(
            obj.location, f'Duplicate parameters: {strlist(dupes)}'
        )


class UnsizedCArray(LocationError):

    def __init__(self, location):
        super().__init__(location, 'Missing size in carray')


class EmptyArray(LocationError):

    def __init__(self, location):
        super().__init__(location, 'Array has no elements')


class ImpossibleLookup(LocationError):

    def __init__(self, location):
        super().__init__(location, 'Cannot lookup attributes in this object')


class ImpossibleReflection(LocationError):

    def __init__(self, location):
        super().__init__(location, 'Cannot reflect on this object')


class ImpossibleCompileTimeEvaluation(LocationError):

    def __init__(self, location):
        super().__init__(
            location, 'Cannot evaluate expression at compile time'
        )


class IndexOutOfBounds(LocationError):

    def __init__(self, location):
        super().__init__(location, 'Index out of bounds')


class NoSuchField(LocationError):

    def __init__(self, location, field_name):
        super().__init__(location, f'No such field {field_name}')


class UnsupportedPlatformIntegerSize(SylvaError):

    def __init__(self, size):
        super().__init__(f'Unsupported platform integer size {size}')

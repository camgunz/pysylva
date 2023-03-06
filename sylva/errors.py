from .utils import bits_required_for_int, strlist


class SylvaError(Exception):

    def pformat(self):
        return f'[Error: {self}]'


class EOF(SylvaError):
    pass


class MutatingBuiltins(SylvaError):

    def __init__(self, builtin_module_statements):
        super().__init__(
            'Cannot modify builtins:\n' + '\n'.join([
                f'\t{module_name}: {location.pformat()}' for location,
                module_name in builtin_module_statements
            ])
        )


class CircularDependency(SylvaError):

    def __init__(self, module, seen):
        super().__init__(f'Circular dependency: {module} cannot be in {seen}')


class UnsupportedPlatformIntegerSize(SylvaError):

    def __init__(self, size):
        super().__init__(f'Unsupported platform integer size {size}')


class LocationError(SylvaError):

    def __init__(self, location, message):
        self.location = location
        SylvaError.__init__(self, message)

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
        LocationError.__init__(
            self,
            token.location,
            (
                f'Unexpected token type {token.token_type} ({token}); '
                f'expected: {strlist(expected_token_types)}'
            )
        )


class UnexpectedTokenCategory(LocationError):

    def __init__(self, token, expected_token_categories):
        LocationError.__init__(
            self,
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
        LocationError.__init__(
            self,
            location,
            (
                f'Unexpected token {token}; '
                f'expected: {strlist(expected_tokens)}'
            )
        )


class SignedSizeError(LocationError):

    def __init__(self, location):
        LocationError.__init__(
            self, location, 'Size must be an unsigned integer'
        )


class LiteralParseFailure(LocationError):

    def __init__(self, literal_type, token, message=None):
        name = literal_type.__name__
        message = f': {message}' if message else ''
        LocationError.__init__(
            self,
            token.location,
            f'Unable to parse {token.value} as {name}{message}'
        )


class InvalidOperatorExpansion(LocationError):

    def __init__(self, location, message):
        LocationError.__init__(
            self, location, f'Invalid operator expansion: {message}'
        )


class InvalidExpressionType(LocationError):

    def __init__(self, location, expected):
        LocationError.__init__(
            self, location, f'Invalid expression type; expected {expected}'
        )


class InvalidExpression(LocationError):

    def __init__(self, location):
        LocationError.__init__(self, location, 'Invalid expression')


class EmptyExpression(LocationError):

    def __init__(self, location):
        LocationError.__init__(self, location, 'Empty expression')


class InvalidOperatorArity(LocationError):

    def __init__(self, location, expected_arity):
        LocationError.__init__(
            self, location, f'Expected {expected_arity.name.lower()} operator'
        )


class UndefinedSymbol(LocationError):

    def __init__(self, location, name):
        LocationError.__init__(self, location, f'Undefined symbol {name}')


class NoSuchAttribute(LocationError):

    def __init__(self, location, name):
        LocationError.__init__(self, location, f'No such field {name}')


class DuplicateDefinition(LocationError):

    def __init__(self, name, location, existing_location):
        LocationError.__init__(
            self,
            location,
            f'"{name}" already defined: [{existing_location.shorthand}]'
        )


class RedefinedBuiltIn(LocationError):

    def __init__(self, definition):
        LocationError.__init__(
            self,
            definition.location,
            f'Cannot redefine builtin "{definition.name}"'
        )


class DefinitionViolation(LocationError):

    def __init__(self, location, name):
        LocationError.__init__(
            self, location, f'Cannot define "{name}" in external module'
        )


class MissingRequirements(SylvaError):

    def __init__(self, missing_requirements):
        error_msg = (
            'Missing requirement'
            if len(missing_requirements) == 1 else 'Missing requirements'
        )
        SylvaError.__init__(
            self,
            '\n\n'.join([ # yapf: disable
                (
                    f'{req.location.pformat()}'
                    '\n'
                    f'[Error: {req.location.shorthand}] Missing requirement'
                )
                for req in missing_requirements
            ]) + '\n'
        )

    def pformat(self):
        return str(self)


class CyclicRequirements(SylvaError):

    def __init__(self, requirements_chain):
        SylvaError.__init__(
            self,
            f'Requirements cycle detected: {" -> ".join(requirements_chain)}'
        )


class NoSuchModule(LocationError):

    def __init__(self, location, module_name):
        LocationError.__init__(self, location, f'No such module {module_name}')


class RedundantAlias(LocationError):

    def __init__(self, location, name):
        LocationError.__init__(
            self, location, f'Alias for {name} is redundant'
        )


class DuplicateAlias(LocationError):

    def __init__(self, location, existing_location, name):
        LocationError.__init__(
            self,
            location,
            f'Alias {name} already defined at {existing_location.shorthand}'
        )


class EmptyVariant(LocationError):

    def __init__(self, variant):
        LocationError.__init__(self, variant.location, 'Variant has no fields')


class DuplicateVariantFields(LocationError):

    def __init__(self, name, variant, dupes):
        LocationError.__init__(
            self,
            variant.location,
            f'Duplicate fields in {name}: {strlist(dupes)}'
        )


class DuplicateEnumFields(LocationError):

    def __init__(self, name, enum, dupes):
        LocationError.__init__(
            self,
            enum.location,
            f'Duplicate fields in {name}: {strlist(dupes)}'
        )


class EmptyEnum(LocationError):

    def __init__(self, location):
        LocationError.__init__(self, location, 'Enum has no fields')


class InconsistentEnumMemberTypes(LocationError):

    def __init__(self, enum):
        LocationError.__init__(
            self, enum.location, f'Unexpected enum type: expected {enum.type}'
        )


class MismatchedRangeTypes(LocationError):

    def __init__(self, location, min_type, max_type):
        LocationError.__init__(
            self, location, f'Mismatched range types: {min_type} {max_type}'
        )


class InvalidRangeValue(LocationError):

    def __init__(self, location, value, min, max):
        LocationError.__init__(
            self,
            location,
            f'Invalid range value "{value}", must be > {min} and < {max}'
        )


class InconsistentElementType(LocationError):

    def __init__(self, location, type):
        LocationError.__init__(
            self, location, f'Unexpected element type: expected {type}'
        )


class MismatchedTypeParams(LocationError):

    def __init__(self, location, type_params):
        LocationError.__init__(
            self,
            location,
            (
                'Mismatched type params, expected '
                f'{strlist([p.name for p in type_params])}'
            )
        )


class DuplicateFields(LocationError):

    def __init__(self, obj, dupes):
        LocationError.__init__(
            self, obj.location, f'Duplicate fields: {strlist(dupes)}'
        )


class DuplicateParameters(LocationError):

    def __init__(self, obj, dupes):
        LocationError.__init__(
            self, obj.location, f'Duplicate parameters: {strlist(dupes)}'
        )


class UnsizedCArray(LocationError):

    def __init__(self, location):
        LocationError.__init__(self, location, 'Missing size in carray')


class EmptyArray(LocationError):

    def __init__(self, location):
        LocationError.__init__(self, location, 'Array has no elements')


class ImpossibleLookup(LocationError):

    def __init__(self, location):
        LocationError.__init__(
            self, location, 'Cannot lookup attributes in this object'
        )


class ImpossibleReflection(LocationError):

    def __init__(self, location):
        LocationError.__init__(self, location, 'Cannot reflect on this object')


class ImpossibleCompileTimeEvaluation(LocationError):

    def __init__(self, location):
        LocationError.__init__(
            self, location, 'Cannot evaluate expression at compile time'
        )


class IndexOutOfBounds(LocationError):

    def __init__(self, location):
        LocationError.__init__(self, location, 'Index out of bounds')


class NoSuchField(LocationError):

    def __init__(self, location, field_name):
        LocationError.__init__(self, location, f'No such field {field_name}')


class InvalidParameterization(LocationError):

    def __init__(self, location, msg):
        LocationError.__init__(self, location, msg)


class InvalidRuneValue(LocationError):

    def __init__(self, location, msg):
        LocationError.__init__(self, location, msg)


class CBitFieldSizeExceeded(LocationError):

    def __init__(self, location, value, field_size):
        LocationError.__init__(
            self,
            location,
            (
                'cbitfield size exceeded; '
                f'{value} requires {bits_required_for_int(value)}, '
                f'has {field_size}'
            )
        )

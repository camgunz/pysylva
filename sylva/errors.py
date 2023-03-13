from pathlib import Path

from sylva.req import Req
from sylva.utils import bits_required_for_int, strlist


class SylvaError(Exception):

    def pformat(self):
        return f'[Error: {self}]'


class EOF(SylvaError):
    pass


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


class UnexpectedToken(LocationError):

    def __init__(self, location, token, expected_tokens):
        token = f"'{token}'" if token == '"' else f'"{token}"'
        expected_tokens = strlist(expected_tokens)
        LocationError.__init__(
            self,
            location,
            f'Unexpected token {token}; expected: {expected_tokens}'
        )


class UnexpectedCharacter(LocationError):

    def __init__(self, location, char, allowed_chars):
        char = f"'{char}'" if char == '"' else f'"{char}"'
        allowed_chars = strlist(allowed_chars)
        LocationError.__init__(
            self,
            location,
            f'Unexpected character {char}; allowed: {allowed_chars}'
        )


class LiteralParseFailure(LocationError):

    def __init__(self, literal_type, token, message=None):
        name = literal_type.__name__
        message = f': {message}' if message else ''
        LocationError.__init__(
            self,
            token.location,
            f'Unable to parse {token.value} as {name}: {message}'
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

    def __init__(self, location, name):
        LocationError.__init__(
            self, location, f'Cannot redefine builtin "{name}"'
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
                    f'[Error: {req.location.shorthand}] {error_msg}'
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


class InvalidArraySize(LocationError):

    def __init__(self, location):
        LocationError.__init__(
            self, location, 'Array element counts must be greater than zero'
        )


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


class IntSizeExceeded(LocationError):

    def __init__(self, location, value, field_size):
        LocationError.__init__(
            self,
            location,
            (
                'int size exceeded; '
                f'{value} requires {bits_required_for_int(value)}, '
                f'has {field_size}'
            )
        )


class NoSuchUnaryOperator(LocationError):

    def __init__(self, location, op):
        LocationError.__init__(self, location, f'No such unary operator {op}')


class InvalidMainPackageType(SylvaError):

    def __init__(self, package_path: Path, package_type: str):
        SylvaError.__init__(
            self,
            f'Package {str(package_path)} has invalid main package type '
            f'{package_type}, expected one of "bin" or "lib"'
        )


class NoUsableCLibTargets(SylvaError):

    def __init__(self, package_name: str, arch: str, os: str):
        SylvaError.__init__(
            self,
            f'No usable targets for {package_name} found for {arch}-{os}'
        )


class OutOfOrderPackageModules(LocationError):

    def __init__(self, package_name: str, module_name: str, req: Req):
        LocationError.__init__(
            self,
            req.location,
            f'Module {module_name} in {package_name} requires in-package '
            f"module {req.name} but it's not yet been processed"
        )

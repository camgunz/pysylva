import ctypes


class SylvaType:
    pass


class SylvaMetaType(SylvaType):
    pass


class BaseArray(SylvaMetaType):

    def __init__(self, location, element_type, element_count):
        self.location = location
        self.element_type = element_type
        self.element_count = element_count

    def __repr__(self):
        return '%s(%r, %r, %r)' % (
            type(self).__name__,
            self.location,
            self.element_type,
            self.element_count
        )

    def __str__(self):
        if self.element_count:
            return (
                f'<{type(self).__name__} '
                f'[{self.element_type} * {self.element_count}]>'
            )
        return f'<{type(self).__name__} [{self.element_type}...]>'


class Array(BaseArray):
    pass


class CArray(BaseArray):
    pass


class CBitField(SylvaMetaType):

    __slots__ = ('location', 'field_type', 'field_size')

    def __init__(self, location, field_type, field_size):
        self.location = location
        self.field_type = field_type
        self.field_size = field_size

    def __repr__(self):
        return 'CBitField(%r, %r, %r)' % (
            self.location,
            self.field_type,
            self.field_size
        )

    def __str__(self):
        return f'<CBitField {self.field_type}:{self.field_size}>'


class Interface(SylvaMetaType):

    __slots__ = ('location', 'name', 'function_types', 'functions')

    def __init__(self, location, name, function_types, functions):
        self.location = location
        self.name = name
        self.function_types = function_types
        self.functions = functions

    def __repr__(self):
        return 'Interface(%r, %r, %r, %r)' % (
            self.location,
            self.name,
            self.function_types,
            self.functions
        )

    def __str__(self):
        return f'<Interface {self.name} {self.function_types} {self.functions}>'


class BaseStruct(SylvaMetaType):

    __slots__ = ('location', 'name', 'type_params', 'fields')

    def __init__(self, location, name, type_params, fields):
        self.location = location
        self.name = name
        self.type_params = type_params
        self.fields = fields

    def __repr__(self):
        prefix = 'Param' if self.type_params else ''
        return '%s%s(%r, %r, %r)' % (
            prefix,
            type(self).__name__,
            self.location,
            self.name,
            self.fields
        )

    def __str__(self):
        type_name = 'ParamStruct' if self.type_params else 'Struct'
        fields = ', '.join([f'{name}: {type}' for name, type in self.fields.items()])
        return f'<{type_name} {self.name} {{{fields}}}>'


class Struct(BaseStruct):
    __slots__ = ('location', 'name', 'type_params', 'fields')


class CStruct(BaseStruct):

    __slots__ = ('location', 'name', 'type_params', 'fields')

    def __init__(self, location, fields, name=None):
        super().__init__(location, name, [], fields)


class Variant(SylvaMetaType):

    __slots__ = ('location', 'name', 'fields')

    def __init__(self, location, name, fields):
        self.location = location
        self.name = name
        self.fields = fields

    def __repr__(self):
        return 'Variant(%r, %r, %r)' % (
            self.location,
            self.name,
            self.fields
        )

    def __str__(self):
        fields = self.fields or {}
        fields = ', '.join([f'{name}: {type}' for name, type in fields.items()])
        return f'<Variant {self.name} {{{fields}}}>'


class CUnion(SylvaMetaType):

    __slots__ = ('location', 'name', 'fields')

    def __init__(self, location, fields, name=None):
        self.location = location
        self.name = name
        self.fields = fields

    def __repr__(self):
        return 'CUnion(%r, %r, %r)' % (
            self.location,
            self.name,
            self.fields
        )

    def __str__(self):
        fields = ', '.join([f'{name}: {type}' for name, type in self.fields.items()])
        name = self.name if self.name else '(anonymous)'
        return f'<CUnion {name} {{{fields}}}>'


class BaseFunctionType(SylvaMetaType):

    __slots__ = ('location', 'parameters', 'return_type', 'name')

    def __init__(self, location, parameters, return_type, name=None):
        self.location = location
        self.parameters = parameters
        self.return_type = return_type
        self.name = name

    def __repr__(self):
        return '%s(%r, %r, %r, %r)' % (
            type(self).__name__,
            self.location,
            self.parameters,
            self.return_type,
            self.name
        )

    def __str__(self):
        name = self.name if self.name else ''
        parameters = ', '.join([f'{n}: {t}' for n, t in self.parameters])
        return_type = f': {self.return_type}' if self.return_type else ''
        return f'<{type(self).__name__} {name}({parameters}){return_type}>'


class FunctionType(BaseFunctionType):
    __slots__ = ('location', 'parameters', 'return_type', 'name')


class CFunctionType(BaseFunctionType):
    __slots__ = ('location', 'parameters', 'return_type', 'name')


class CBlockFunctionType(BaseFunctionType):
    __slots__ = ('location', 'parameters', 'return_type', 'name')


class BaseFunction(SylvaMetaType):

    __slots__ = ('location', 'parameters', 'return_type', 'code', 'name')

    def __init__(self, location, parameters, return_type, code, name=None):
        self.location = location
        self.parameters = parameters
        self.return_type = return_type
        self.code = code
        self.name = name

    def __repr__(self):
        return '%s(%r, %r, %r, %r, %r)' % (
            type(self).__name__,
            self.location,
            self.parameters,
            self.return_type,
            self.name,
            self.code,
        )

    def __str__(self):
        name = self.name if self.name else ''
        parameters = ', '.join([f'{n}: {t}' for n, t in self.parameters])
        return_type = f': {self.return_type}' if self.return_type else ''
        return f'<{type(self).__name__} {name}({parameters}){return_type}>'



class Function(BaseFunction):
    __slots__ = ('location', 'parameters', 'return_type', 'code', 'name')


class CFunction(BaseFunction):

    __slots__ = ('location', 'parameters', 'return_type', 'code', 'name')

    def __init__(self, location, parameters, return_type, name=None):
        super().__init__(
            location, parameters, return_type, code=None, name=name
        )


class CPtr(SylvaMetaType):

    __slots__ = ('location', 'referenced_type')

    def __init__(self, location, referenced_type, referenced_type_is_mutable,
                 is_mutable):
        self.location = location
        self.referenced_type = referenced_type
        self.referenced_type_is_mutable = referenced_type_is_mutable
        self.is_mutable = is_mutable

    def __repr__(self):
        return 'CPtr(%r, %r, %r, %r)' % (
            self.location,
            self.referenced_type,
            self.referenced_type_is_mutable,
            self.is_mutable
        )

    def __str__(self):
        return (
            f'<CPtr {self.referenced_type} {self.referenced_type_is_mutable} '
            f'{self.is_mutable}>'
        )


class CVoid(SylvaType):
    pass


class Scalar(SylvaType):
    def __repr__(self):
        return f'{type(self).__name__}()'


# Booleans are the native integer type
class Boolean(Scalar):
    pass


class Rune(Scalar):
    pass


class String(Scalar):
    pass


class CString(Scalar):
    pass


class Decimal(Scalar):
    pass


class Complex(Scalar):

    __slots__ = ('bits',)

    def __init__(self, bits):
        self.bits = bits

    def __repr__(self):
        return f'{type(self).__name__}(bits={self.bits})'


class Float(Scalar):

    __slots__ = ('bits',)

    def __init__(self, bits):
        self.bits = bits

    def __repr__(self):
        return f'{type(self).__name__}(bits={self.bits})'


class Integer(Scalar):

    __slots__ = ('bits', 'signed')

    def __init__(self, bits, signed):
        self.bits = bits
        self.signed = signed

    def __repr__(self):
        prefix = 'U' if not self.signed else ''
        return f'{prefix}{type(self).__name__}(bits={self.bits})'


class ReferencePointer(SylvaMetaType):

    def __init__(self, location, referenced_type, is_mutable):
        self.location = location
        self.referenced_type = referenced_type
        self.is_mutable = is_mutable

    def __repr__(self):
        return 'ReferencePointer(%r, %r, %r)' % (
            self.location,
            self.referenced_type,
            self.is_mutable
        )

    def __str__(self):
        return f'<ReferencePointer {self.referenced_type}>'


class OwnedPointer(SylvaMetaType):

    def __init__(self, location, referenced_type):
        self.location = location
        self.referenced_type = referenced_type

    def __repr__(self):
        return 'OwnedPointer(%r, %r)' % (self.location, self.referenced_type)

    def __str__(self):
        return f'<OwnedPointer {self.referenced_type}>'


BUILTINS = {
    # 'array': Array(), # meta
    # 'iface': Interface(), # meta
    # 'struct': Struct(), # meta
    # 'variant': Variant(), # meta
    # 'fntype': FunctionType(), # meta
    # 'fn': Function(), # meta

    # 'carray': CArray(), # meta
    # 'cstruct': CStruct(), # meta
    # 'cunion': ..., # meta
    # 'cfntype': CFunctionType(), # meta
    # 'cblockfntype': CBlockFunctionType(), # meta
    # 'cfn': CFunction(), # meta
    # 'cptr': CPtr(), # meta

    'cvoid': CVoid(),
    'bool': Boolean(),
    'c16': Complex(16),
    'c32': Complex(32),
    'c64': Complex(64),
    'c128': Complex(128),
    'cstr': CString(),
    'dec': Decimal(),
    'f16': Float(16),
    'f32': Float(32),
    'f64': Float(64),
    'f128': Float(128),
    'int': Integer(ctypes.sizeof(ctypes.c_int) * 8, signed=True),
    'i8': Integer(8, signed=True),
    'i16': Integer(16, signed=True),
    'i32': Integer(32, signed=True),
    'i64': Integer(64, signed=True),
    'i128': Integer(128, signed=True),
    'rune': Rune(),
    'str': String(),
    'uint': Integer(ctypes.sizeof(ctypes.c_int) * 8, signed=False),
    'u8': Integer(8, signed=False),
    'u16': Integer(16, signed=False),
    'u32': Integer(32, signed=False),
    'u64': Integer(64, signed=False),
    'u128': Integer(128, signed=False),
}

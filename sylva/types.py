import ctypes


class SylvaType:

    @property
    def type_name(self):
        return type(self).__name__

    @property
    def name(self):
        return self.type_name

    def __repr__(self):
        return f'{self.name}()'

    def __str__(self):
        return f'<{self.name}>'


class SylvaMetaType(SylvaType):

    __slots__ = ('location',)

    def __init__(self, location):
        self.location = location


class CBitField(SylvaType):

    __slots__ = ('location', 'bits', 'signed', 'field_size')

    def __init__(self, location, bits, signed, field_size):
        self.location = location
        self.bits = bits
        self.signed = signed
        self.field_size = field_size

    def __repr__(self):
        return 'CBitField(%r, %r, %r, %r)' % (
            self.location, self.bits, self.signed, self.field_size
        )

    def __str__(self):
        prefix = 'i' if self.signed else 'u'
        return f'<CBitField {prefix}{self.bits}:{self.field_size}>'


class CVoid(SylvaType):
    pass


class Scalar(SylvaType):
    pass


class Boolean(Scalar): # Booleans are the native integer type
    pass


class Rune(Scalar):
    pass


class String(Scalar):
    pass


class CString(Scalar):
    pass


class Numeric(Scalar):
    pass


class SizedNumeric(Numeric):

    __slots__ = ('bits',)

    def __init__(self, bits):
        self.bits = bits

    def __repr__(self):
        return f'{self.type_name}(bits={self.bits})'

    def __str__(self):
        return f'<{self.type_name}{self.bits}>'


class Decimal(Numeric):
    pass


class Complex(SizedNumeric):
    __slots__ = ('bits',)


class Float(SizedNumeric):
    __slots__ = ('bits',)


class Integer(SizedNumeric):

    __slots__ = ('bits', 'signed')

    def __init__(self, bits, signed):
        super().__init__(bits)
        self.signed = signed

    def __repr__(self):
        return f'{self.type_name}(bits={self.bits}, signed={self.signed})'

    def __str__(self):
        prefix = 'U' if not self.signed else ''
        return f'<{prefix}{self.type_name}{self.bits}>'


class BaseArray(SylvaMetaType):

    def __init__(self, location, element_type, element_count):
        super().__init__(location)
        self.element_type = element_type
        self.element_count = element_count

    def __repr__(self):
        return '%s(%r, %r, %r)' % (
            self.type_name,
            self.location,
            self.element_type,
            self.element_count
        )

    def __str__(self):
        if self.element_count:
            return (
                f'<{self.type_name} '
                f'[{self.element_type} * {self.element_count}]>'
            )
        return f'<{self.type_name} [{self.element_type}...]>'


class Array(BaseArray):
    pass


class CArray(BaseArray):
    pass


class Enum(SylvaMetaType):

    __slots__ = ('location', 'values')

    def __init__(self, location, values):
        super().__init__(location)
        self.values = values

    def __repr__(self):
        return 'Enum(%r, %r)' % (self.location, self.values)

    def __str__(self):
        return f'<Enum {self.values}>'


class Range(SylvaMetaType):

    __slots__ = ('location', 'type', 'min', 'max')

    def __init__(self, location, type, min, max):
        super().__init__(location)
        self.type = type
        self.min = min
        self.max = max

    def __repr__(self):
        return 'Range(%r, %r, %r, %s)' % (
            self.location, self.type, self.min, self.max
        )

    def __str__(self):
        return f'<Range {self.type} {self.min}-{self.max}>'


class Interface(SylvaMetaType):

    __slots__ = ('location', 'function_types', 'functions')

    def __init__(self, location, function_types, functions):
        super().__init__(location)
        self.function_types = function_types
        self.functions = functions

    def __repr__(self):
        return 'Interface(%r, %r, %r)' % (
            self.location, self.function_types, self.functions
        )

    def __str__(self):
        return f'<Interface {self.function_types} {self.functions}>'


class BaseStruct(SylvaMetaType):

    __slots__ = ('location', 'type_params', 'fields')

    def __init__(self, location, type_params, fields):
        super().__init__(location)
        self.type_params = type_params
        self.fields = fields

    def __repr__(self):
        return '%s(%r, %r, %r)' % (
            self.type_name, self.location, self.type_params, self.fields
        )

    def __str__(self):
        type_name = 'ParamStruct' if self.type_params else 'Struct'
        fields = ', '.join([
            f'{name}: {type}' for name, type in self.fields.items()
        ])
        return f'<{type_name} {{{fields}}}>'


class Struct(BaseStruct):
    __slots__ = ('location', 'type_params', 'fields')


class CStruct(BaseStruct):

    __slots__ = ('location', 'type_params', 'fields')

    def __init__(self, location, fields):
        super().__init__(location, [], fields)


class Variant(SylvaMetaType):

    __slots__ = ('location', 'fields')

    def __init__(self, location, fields):
        super().__init__(location)
        self.fields = fields

    def __repr__(self):
        return 'Variant(%r, %r)' % (self.location, self.fields)

    def __str__(self):
        fields = self.fields or {}
        fields = ', '.join([
            f'{name}: {type}' for name, type in fields.items()
        ])
        return f'<Variant {{{fields}}}>'


class CUnion(SylvaMetaType):

    __slots__ = ('location', 'fields')

    def __init__(self, location, fields):
        super().__init__(location)
        self.fields = fields

    def __repr__(self):
        return 'CUnion(%r, %r)' % (self.location, self.fields)

    def __str__(self):
        fields = ', '.join([
            f'{name}: {type}' for name, type in self.fields.items()
        ])
        return f'<CUnion {{{fields}}}>'


class BaseFunctionType(SylvaMetaType):

    __slots__ = ('location', 'parameters', 'return_type')

    def __init__(self, location, parameters, return_type):
        super().__init__(location)
        self.parameters = parameters
        self.return_type = return_type

    def __repr__(self):
        return '%s(%r, %r, %r)' % (
            self.type_name,
            self.location,
            self.parameters,
            self.return_type,
        )

    def __str__(self):
        parameters = ', '.join([
            f'{n}: {t}' for n, t in self.parameters.items()
        ])
        return_type = f': {self.return_type}' if self.return_type else ''
        return f'<{self.type_name} ({parameters}){return_type}>'


class FunctionType(BaseFunctionType):
    __slots__ = ('location', 'parameters', 'return_type')


class CFunctionType(BaseFunctionType):
    __slots__ = ('location', 'parameters', 'return_type')


class CBlockFunctionType(BaseFunctionType):
    __slots__ = ('location', 'parameters', 'return_type')


class BaseFunction(SylvaMetaType):

    __slots__ = ('location', 'parameters', 'return_type', 'code')

    def __init__(self, location, parameters, return_type, code):
        super().__init__(location)
        self.parameters = parameters
        self.return_type = return_type
        self.code = code

    def __repr__(self):
        return '%s(%r, %r, %r, %r)' % (
            self.type_name,
            self.location,
            self.parameters,
            self.return_type,
            self.code,
        )

    def __str__(self):
        parameters = ', '.join([
            f'{n}: {t}' for n, t in self.parameters.items()
        ])
        return_type = f': {self.return_type}' if self.return_type else ''
        return f'<{self.type_name} ({parameters}){return_type}>{{{self.code}}}'


class Function(BaseFunction):
    __slots__ = ('location', 'parameters', 'return_type', 'code')


class CFunction(BaseFunction):

    __slots__ = ('location', 'parameters', 'return_type', 'code')

    def __init__(self, location, parameters, return_type):
        super().__init__(location, parameters, return_type, code=None)


class CPtr(SylvaMetaType):

    __slots__ = ('location', 'referenced_type')

    def __init__(
        self,
        location,
        referenced_type,
        referenced_type_is_mutable,
        is_mutable
    ):
        super().__init__(location)
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
        ref_is_mutable = self.referenced_type_is_mutable
        return (
            f'<CPtr{"!" if self.is_mutable else ""} '
            f'{self.referenced_type}{"!" if ref_is_mutable else ""}>'
        )


class ReferencePointer(SylvaMetaType):

    def __init__(self, location, referenced_type, is_mutable):
        super().__init__(location)
        self.referenced_type = referenced_type
        self.is_mutable = is_mutable

    def __repr__(self):
        return 'ReferencePointer(%r, %r, %r)' % (
            self.location, self.referenced_type, self.is_mutable
        )

    def __str__(self):
        return f'<ReferencePointer {self.referenced_type}>'


class OwnedPointer(SylvaMetaType):

    def __init__(self, location, referenced_type):
        super().__init__(location)
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
    'int': Integer(ctypes.sizeof(ctypes.c_size_t) * 8, signed=True),
    'i8': Integer(8, signed=True),
    'i16': Integer(16, signed=True),
    'i32': Integer(32, signed=True),
    'i64': Integer(64, signed=True),
    'i128': Integer(128, signed=True),
    'rune': Rune(),
    'str': String(),
    'uint': Integer(ctypes.sizeof(ctypes.c_size_t) * 8, signed=False),
    'u8': Integer(8, signed=False),
    'u16': Integer(16, signed=False),
    'u32': Integer(32, signed=False),
    'u64': Integer(64, signed=False),
    'u128': Integer(128, signed=False),
}

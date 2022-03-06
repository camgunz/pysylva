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
        return '{type(self).__name__(%r, %r, %r)' % (
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
        return f'<{type(self).__name__} [{self.element_type}]>'


class Array(BaseArray):
    pass


class CArray(BaseArray):
    pass


class Interface(SylvaMetaType):
    location = None
    name = None
    function_types = None
    functions = None

    def __repr__(self):
        return 'Interface(%r, %r, %r, %r)' % (
            self.location,
            self.name,
            self.function_types,
            self.functions
        )

    def __str__(self):
        return f'<Interface {self.name} {self.function_types} {self.functions}>'

    def parse(self, name, parser):
        location, function_types, functions = parser.parse_interface()
        return type(
            name,
            (type(self),),
            {
                'location': location,
                'function_types': function_types,
                'functions': functions,
            }
        )


class BaseStruct(SylvaMetaType):
    location = None
    name = None
    type_params = None
    fields = None

    def __repr__(self):
        type_name = 'ParamStruct' if self.type_params else 'Struct'
        return '%s(%r, %r, %r)' % (
            type_name,
            self.location,
            self.name,
            self.fields
        )

    def __str__(self):
        type_name = 'ParamStruct' if self.type_params else 'Struct'
        fields = ', '.join([f'{name}: {type}' for name, type in self.fields])
        return f'<{type_name} {self.name} {{{fields}}}>'

    def parse(self, name, parser):
        location, type_params, fields = parser.parse_struct_type()
        return type(
            name,
            (type(self),),
            {
                'location': location,
                'type_params': type_params,
                'fields': fields,
            }
        )


class Struct(BaseStruct):
    pass


class CStruct(BaseStruct):
    pass


class Variant(SylvaMetaType):
    location = None
    name = None
    fields = None

    def __repr__(self):
        return 'Variant(%r, %r, %r)' % (
            self.location,
            self.name,
            self.fields
        )

    def __str__(self):
        fields = self.fields or []
        fields = ', '.join([f'{name}: {type}' for name, type in fields])
        return f'<Variant {self.name} {{{fields}}}>'

    def parse(self, name, parser):
        location, fields = parser.parse_variant_type()
        return type(
            name,
            (type(self),),
            {
                'location': location,
                'fields': fields,
            }
        )


class CUnion(SylvaMetaType):
    pass


class BaseFunctionType(SylvaMetaType):

    location = None
    name = None
    parameters = None
    return_type = None

    def __repr__(self):
        return '%s(%r, %r, %r)' % (
            type(self).__name__,
            self.name,
            self.parameters,
            self.return_type
        )

    def __str__(self):
        parameters = ', '.join([f'{n}: {t}' for n, t in self.parameters])
        if self.return_type:
            return (
                f'<{type(self).__name__} {self.name}({parameters}): '
                '{self.return_type}>'
            )
        return f'<{type(self).__name__} {self.name}({parameters})>'

    def parse(self, name, parser):
        location, parameters, return_type = parser.parse_function_type()
        return type(
            name,
            (type(self),),
            {
                'location': location,
                'parameters': parameters,
                'return_type': return_type,
            }
        )


class FunctionType(BaseFunctionType):
    pass


class CFunctionType(BaseFunctionType):
    pass


class CBlockFunctionType(BaseFunctionType):
    pass


class BaseFunction(SylvaMetaType):
    location = None
    name = None
    parameters = None
    return_type = None
    code = None

    def parse(self, name, parser):
        location, parameters, return_type, code = parser.parse_function()
        return type(
            name,
            (type(self),),
            {
                'location': location,
                'parameters': parameters,
                'return_type': return_type,
                'code': code,
            }
        )

    def __repr__(self):
        return '%s(%r, %r, %r)' % (
            type(self).__name__,
            self.name,
            self.parameters,
            self.return_type
        )

    def __str__(self):
        parameters = ', '.join([f'{n}: {t}' for n, t in self.parameters])
        if self.return_type:
            return (
                f'<{type(self).__name__} {self.name}({parameters}): '
                f'{self.return_type}>'
            )
        return f'<{type(self).__name__} {self.name}({parameters})>'


class Function(BaseFunction):
    pass


class CFunction(BaseFunction):
    pass


class CPtr(SylvaMetaType):
    pass


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


BUILTINS = {
    # 'array': Array(), # meta
    # 'carray': CArray(), # meta
    # 'iface': Interface(), # meta
    # 'struct': Struct(), # meta
    # 'cstruct': CStruct(), # meta
    # 'variant': Variant(), # meta
    # 'cunion': ..., # meta
    # 'fntype': FunctionType(), # meta
    # 'cfntype': CFunctionType(), # meta
    # 'cblockfntype': CBlockFunctionType(), # meta
    # 'fn': Function(), # meta
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
    'i8': Integer(8, signed=True),
    'i16': Integer(16, signed=True),
    'i32': Integer(32, signed=True),
    'i64': Integer(64, signed=True),
    'i128': Integer(128, signed=True),
    'rune': Rune(),
    'str': String(),
    'u8': Integer(8, signed=False),
    'u16': Integer(16, signed=False),
    'u32': Integer(32, signed=False),
    'u64': Integer(64, signed=False),
    'u128': Integer(128, signed=False),
}

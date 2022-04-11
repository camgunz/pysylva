import ctypes

from functools import cache

from llvmlite import ir

from . import errors, utils


def round_up_to_multiple(x, base):
    rem = x % base
    if rem == 0:
        return x
    return x + base - rem


class SylvaType:

    @property
    def name(self):
        return type(self).__name__

    def __repr__(self):
        return f'{self.name}()'

    def __str__(self):
        return f'<{self.name}>'

    # pylint: disable=no-self-use
    def check(self):
        return []


class SylvaLLVMType(SylvaType):

    @cache
    def make_constant(self, module, value):
        return self.get_llvm_type(module)(value)

    @cache
    def get_alignment(self, module):
        return self.get_llvm_type(module).get_abi_alignment(module.target.data)

    @cache
    def get_size(self, module):
        return self.get_llvm_type(module).get_abi_size(module.target.data)

    @cache
    def get_pointer(self, module):
        return self.get_llvm_type(module).as_pointer()

    @cache
    def get_llvm_type(self, module):
        raise NotImplementedError()


class ParamSylvaType(SylvaType):

    __slots__ = ('location',)

    def __init__(self, location):
        self.location = location


class MetaSylvaType(SylvaType):

    __slots__ = ('location',)

    def __init__(self, location):
        self.location = location

    @property
    def names(self):
        raise NotImplementedError()

    @property
    def types(self):
        raise NotImplementedError()

    def check(self):
        type_errors = []

        dupes = utils.get_dupes(self.names)
        if dupes:
            type_errors.append(errors.DuplicateFields(self, dupes))

        return type_errors

    def resolve_self_references(self, name):
        missing_field_errors = []

        for field_type in self.types:
            if not isinstance(field_type, BasePointer):
                continue
            if not isinstance(field_type.referenced_type, DeferredTypeLookup):
                continue
            pointer = field_type
            deferred_lookup = pointer.referenced_type
            if deferred_lookup.value == name:
                pointer.referenced_type = self
            else:
                missing_field_errors.append(
                    errors.UndefinedSymbol(
                        deferred_lookup.location, deferred_lookup.value
                    )
                )

        return missing_field_errors


class MetaSylvaLLVMType(MetaSylvaType, SylvaLLVMType):
    __slots__ = ('location',)


class DeferredTypeLookup(SylvaType):

    __slots__ = (
        'location',
        'value',
    )

    def __init__(self, location, value):
        self.location = location
        self.value = value

    def __repr__(self):
        return '%s(%r, %r)' % (self.value, self.location, self.value)

    def __str__(self):
        return f'<{self.name} {self.value}>'


class CBitField(SylvaLLVMType):

    __slots__ = ('location', 'bits', 'signed', 'field_size')

    def __init__(self, location, bits, signed, field_size):
        self.location = location
        self.bits = bits
        self.signed = signed
        self.field_size = field_size

    def __repr__(self):
        return '%s(%r, %r, %r, %r)' % (
            self.name, self.location, self.bits, self.signed, self.field_size
        )

    def __str__(self):
        prefix = 'i' if self.signed else 'u'
        return f'<{self.name} {prefix}{self.bits}:{self.field_size}>'

    @cache
    def get_llvm_type(self, module):
        return ir.IntType(self.bits)


class CVoid(SylvaLLVMType):

    @cache
    def get_llvm_type(self, module):
        return ir.VoidType()


class Scalar(SylvaLLVMType):
    pass


class Boolean(Scalar):

    @cache
    def get_llvm_type(self, module):
        return ir.IntType(8)


class Rune(Scalar):

    @cache
    def get_llvm_type(self, module):
        return ir.IntType(32)


class BaseString(Scalar):

    @cache
    def get_llvm_type(self, module):
        return ir.PointerType(ir.IntType(8))


class String(BaseString):
    pass


class CString(BaseString):
    pass


class Numeric(Scalar):
    pass


class SizedNumeric(Numeric):

    __slots__ = ('bits',)

    def __init__(self, bits):
        self.bits = bits

    def __repr__(self):
        return f'{self.name}(bits={self.bits})'

    def __str__(self):
        return f'<{self.name}{self.bits}>'


class Decimal(Numeric):
    pass


class Complex(SizedNumeric):
    __slots__ = ('bits',)

    @cache
    def get_llvm_type(self, module):
        if self.bits == 8:
            return ir.HalfType()
        if self.bits == 16:
            return ir.FloatType()
        if self.bits == 32:
            return ir.DoubleType()
        # [NOTE] llvmlite won't do float types > 64 bits
        if self.bits == 64:
            return ir.DoubleType()
        if self.bits == 128:
            return ir.DoubleType()


class Float(SizedNumeric):
    __slots__ = ('bits',)

    @cache
    def get_llvm_type(self, module):
        # [NOTE] llvmlite won't do float types < 16 bits
        if self.bits == 8:
            return ir.HalfType()
        if self.bits == 16:
            return ir.HalfType()
        if self.bits == 32:
            return ir.FloatType()
        if self.bits == 64:
            return ir.DoubleType()
        # [NOTE] llvmlite won't do float types > 64 bits
        if self.bits == 128:
            return ir.DoubleType()


class Integer(SizedNumeric):

    __slots__ = ('bits', 'signed')

    def __init__(self, bits, signed):
        super().__init__(bits)
        self.signed = signed

    def __repr__(self):
        return f'{self.name}(bits={self.bits}, signed={self.signed})'

    def __str__(self):
        prefix = 'U' if not self.signed else ''
        return f'<{prefix}{self.name}{self.bits}>'

    @cache
    def get_llvm_type(self, module):
        return ir.IntType(self.bits)


class BaseArray(MetaSylvaLLVMType):

    __slots__ = ('location', 'element_type', 'element_count')

    def __init__(self, location, element_type, element_count):
        super().__init__(location)
        self.element_type = element_type
        self.element_count = element_count

    def __repr__(self):
        return '%s(%r, %r, %r)' % (
            self.name, self.location, self.element_type, self.element_count
        )

    def __str__(self):
        if self.element_count:
            return (
                f'<{self.name} [{self.element_type} * {self.element_count}]>'
            )
        return f'<{self.name} [{self.element_type}...]>'

    @property
    def names(self):
        return []

    @property
    def types(self):
        return [self.element_type]

    @cache
    def get_llvm_type(self, module):
        return ir.ArrayType(
            self.element_type.get_llvm_type(module), self.element_count
        )


class Array(BaseArray):
    __slots__ = ('location', 'element_type', 'element_count')


class CArray(BaseArray):
    __slots__ = ('location', 'element_type', 'element_count')

    def __init__(self, location, element_type, element_count):
        super().__init__(location, element_type, element_count)
        if self.element_count is None:
            raise errors.UnsizedCArray(location)


class ConstDef(SylvaLLVMType):

    __slots__ = ('location', 'value')

    def __init__(self, location, value):
        self.location = location
        self.value = value

    def __repr__(self):
        return 'ConstDef(%r, %r)' % (self.location, self.value)

    def __str__(self):
        return f'<ConstDef {self.value}>'


class Enum(MetaSylvaLLVMType):

    __slots__ = ('location', 'values')

    def __init__(self, location, values):
        super().__init__(location)
        self.values = values
        if not self.values:
            raise errors.EmptyEnum(self)

    def __repr__(self):
        return '%s(%r, %r)' % (self.name, self.location, self.values)

    def __str__(self):
        return f'<{self.name} {self.values}>'

    @cache
    def get_llvm_type(self, module):
        return self.values[0].type

    @property
    def names(self):
        return self.values.keys()

    @property
    def types(self):
        return [self.values[0].type]

    def check(self):
        super().check()

        first_type = self.values[0].type
        for value in self.values[1:]:
            if value.type != first_type:
                raise errors.MismatchedEnumMemberType(first_type, value)


class Range(MetaSylvaLLVMType):

    __slots__ = ('location', 'type', 'min', 'max')

    def __init__(self, location, type, min, max):
        super().__init__(location)
        self.type = type
        self.min = min
        self.max = max

    def __repr__(self):
        return '%s(%r, %r, %r, %s)' % (
            self.name, self.location, self.type, self.min, self.max
        )

    def __str__(self):
        return f'<{self.name} {self.type} {self.min}-{self.max}>'

    @property
    def names(self):
        return []

    @property
    def types(self):
        return [self.type]

    @cache
    def get_llvm_type(self, module):
        return self.type.type


class Interface(MetaSylvaType):

    __slots__ = ('location', 'fields')

    def __init__(self, location, fields):
        super().__init__(location)
        self.fields = fields

    def __repr__(self):
        return '%s(%r, %r)' % (self.name, self.location, self.fields)

    def __str__(self):
        return f'<{self.name} {self.fields}>'


class Implementation:

    def __init__(self, location, interface, implementing_type, funcs):
        self.location = location
        self.interface = interface
        self.implementing_type = implementing_type
        self.funcs = funcs

    def __repr__(self):
        return 'Implementation(%r, %r, %r)' % (
            self.interface, self.implementing_type, self.funcs
        )


class BaseStruct(MetaSylvaLLVMType):

    __slots__ = ('location', 'fields', '_llvm_type')

    def __init__(self, location, fields):
        super().__init__(location)
        self.fields = fields
        self._llvm_type = None
        # self._size = 0
        # self._alignment = 1
        # self._offsets = {}
        # for name, type in self.fields:
        #     self._size = round_up_to_multiple(self._size, type.alignment)
        #     self._alignment = max(self._alignment, type.alignment)
        #     self._offsets[name] = self._size
        #     self._size += type.size
        # self._size = round_up_to_multiple(self._size, self._alignment)

    def __repr__(self):
        # return '%s(%r, %r)' % (self.name, self.location, self.fields)
        return 'Struct()'

    def __str__(self):
        # fields = ', '.join([
        #     f'{name}: {type}' for name, type in self.fields.items()
        # ])
        # return f'<{self.name} {{{fields}}}>'
        return '<Struct>'

    @property
    def names(self):
        return self.fields.keys()

    @property
    def types(self):
        return self.fields.values()

    # pylint: disable=arguments-differ
    def get_llvm_type(self, module, name=None):
        if self._llvm_type:
            return self._llvm_type

        if name is None:
            for f in self.fields.values():
                if not isinstance(f, BasePointer):
                    continue
                if not f.referenced_type == self:
                    continue
                raise Exception('Cannot have self-referential struct literals')
            self._llvm_type = ir.LiteralStructType([
                f.get_llvm_type(module) for f in self.fields.values()
            ])
        else:
            struct = module.get_identified_type(name)
            fields = []
            for f in self.fields.values():
                if not isinstance(f, BasePointer):
                    fields.append(f.get_llvm_type(module))
                elif not f.referenced_type == self:
                    fields.append(f.get_llvm_type(module))
                else:
                    fields.append(ir.PointerType(struct))
            struct.set_body(*fields)
            self._llvm_type = struct

        return self._llvm_type


class CStruct(BaseStruct):
    __slots__ = ('location', 'fields')


class Struct(BaseStruct):
    __slots__ = ('location', 'fields')


class ParamStruct(ParamSylvaType):

    __slots__ = ('location', 'type_params', 'fields')

    def __init__(self, location, type_params, fields):
        super().__init__(location)
        self.type_params = type_params
        self.fields = fields

    def __repr__(self):
        return '%s(%r, %r, %r)' % (
            self.name, self.location, self.type_params, self.fields
        )

    def __str__(self):
        fields = ', '.join([
            f'{name}: {type}' for name, type in self.fields.items()
        ])
        return f'<{self.name} {{{fields}}}>'

    def get_struct(self, location, type_args):
        fields = {}
        for field_name, type_param in self.fields.items():
            if isinstance(type_param, str):
                field_type = type_args.get(type_param)
                if field_type is None:
                    raise errors.MissingTypeParam(location, type_param)
                fields[field_name] = field_type
            else:
                fields[field_name] = type_param
        return Struct(location, fields)


class MetaSylvaLLVMUnionType(MetaSylvaLLVMType):

    __slots__ = ('location', 'fields')

    def __init__(self, location, fields):
        super().__init__(location)
        self.fields = fields

    def __repr__(self):
        return '%s(%r, %r)' % (self.name, self.location, self.fields)

    def __str__(self):
        fields = ', '.join([
            f'{name}: {type}' for name, type in self.fields.items()
        ])
        return f'<{self.name} {{{fields}}}>'

    @property
    def names(self):
        return self.fields.keys()

    @property
    def types(self):
        return self.fields.values()

    @cache
    def get_largest_field(self, module):
        fields = list(self.fields.values())
        largest_field = fields[0]
        for field in fields[1:]:
            if field.get_size(module) > largest_field.get_size(module):
                largest_field = field
        return largest_field.get_llvm_type(module)


class Variant(MetaSylvaLLVMUnionType):

    __slots__ = ('location', 'fields')

    def check(self):
        type_errors = super().check()
        type_errors.append(errors.EmptyVariant(self))

        return type_errors

    @cache
    def get_llvm_type(self, module):
        tag_bit_width = round_up_to_multiple(len(self.fields), 8)
        return ir.LiteralStructType([
            self.get_largest_field(module), ir.IntType(tag_bit_width)
        ])


class ParamVariant(ParamSylvaType):

    __slots__ = ('location', 'type_params', 'fields')

    def __init__(self, location, type_params, fields):
        super().__init__(location)
        self.type_params = type_params
        self.fields = fields

    def __repr__(self):
        return '%s(%r, %r, %r)' % (
            self.name, self.location, self.type_params, self.fields
        )

    def __str__(self):
        fields = ', '.join([
            f'{name}: {type}' for name, type in self.fields.items()
        ])
        return f'<{self.name} {{{fields}}}>'

    def get_variant(self, location, type_args):
        fields = {}
        for field_name, type_param in self.fields.items():
            if isinstance(type_param, str):
                field_type = type_args.get(type_param)
                if field_type is None:
                    raise errors.MissingTypeParam(location, type_param)
                fields[field_name] = field_type
            else:
                fields[field_name] = type_param
        return Variant(location, fields)


class CUnion(MetaSylvaLLVMUnionType):

    __slots__ = ('location', 'fields')

    @cache
    def get_llvm_type(self, module):
        return ir.LiteralStructType([self.get_largest_field(module)])


class BaseFunctionType(MetaSylvaLLVMType):

    __slots__ = ('location', 'parameters', 'return_type')

    def __init__(self, location, parameters, return_type):
        super().__init__(location)
        self.parameters = parameters
        self.return_type = return_type

    def __repr__(self):
        return '%s(%r, %r, %r)' % (
            self.name,
            self.location,
            self.parameters,
            self.return_type,
        )

    def __str__(self):
        parameters = ', '.join([
            f'{n}: {t}' for n, t in self.parameters.items()
        ])
        return_type = f': {self.return_type}' if self.return_type else ''
        return f'<{self.name} ({parameters}){return_type}>'

    @property
    def names(self):
        return self.parameters.keys()

    @property
    def types(self):
        return self.parameters.values()

    @cache
    def get_llvm_type(self, module):
        params = []

        for p in self.parameters.values():
            params.append(p.get_llvm_type(module))

        return ir.FunctionType(
            self.return_type.get_llvm_type(module)
            if self.return_type else ir.VoidType(),
            params
        )


class FunctionType(BaseFunctionType):
    __slots__ = ('location', 'parameters', 'return_type')


class CFunctionType(BaseFunctionType):
    __slots__ = ('location', 'parameters', 'return_type')

    @cache
    def get_llvm_type(self, module):
        return super().get_llvm_type(module).as_pointer()


class CBlockFunctionType(BaseFunctionType):
    __slots__ = ('location', 'parameters', 'return_type')


class CFunction(BaseFunctionType):
    __slots__ = ('location', 'parameters', 'return_type')


class Function(BaseFunctionType):

    __slots__ = ('location', 'parameters', 'return_type', 'code')

    def __init__(self, location, parameters, return_type, code):
        super().__init__(location, parameters, return_type)
        self.code = code

    def __repr__(self):
        return '%s(%r, %r, %r, %r)' % (
            self.name,
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
        return f'<{self.name} ({parameters}){return_type}>{{{self.code}}}'


class BasePointer(MetaSylvaLLVMType):

    __slots__ = ('location', 'referenced_type', 'is_mutable')

    def __init__(self, location, referenced_type, is_mutable):
        super().__init__(location)
        self.referenced_type = referenced_type
        self.is_mutable = is_mutable

    def __repr__(self):
        return '%s(%r, %r, is_mutable=%r)' % (
            self.name, self.location, self.referenced_type, self.is_mutable
        )

    def __str__(self):
        suffix = '!' if self.is_mutable else ''
        return f'<{self.name}{suffix} {self.referenced_type}>'

    @property
    def names(self):
        return []

    @property
    def types(self):
        return [self.referenced_type]

    @cache
    def get_llvm_type(self, module):
        return ir.PointerType(self.referenced_type.get_llvm_type(module))


class CPtr(BasePointer):

    __slots__ = (
        'location',
        'referenced_type',
        'referenced_type_is_mutable',
        'is_mutable'
    )

    def __init__(
        self,
        location,
        referenced_type,
        referenced_type_is_mutable,
        is_mutable
    ):
        super().__init__(location, referenced_type, is_mutable)
        self.referenced_type_is_mutable = referenced_type_is_mutable

    def __repr__(self):
        return '%s(%r, %r, %r, %r)' % (
            self.name,
            self.location,
            self.referenced_type,
            self.referenced_type_is_mutable,
            self.is_mutable
        )

    def __str__(self):
        suffix = '!' if self.is_mutable else ''
        ref_suffix = '!' if self.referenced_type_is_mutable else ''
        return f'<{self.name}{suffix} {self.referenced_type}{ref_suffix}>'


class ReferencePointer(BasePointer):
    __slots__ = ('location', 'referenced_type', 'is_mutable')


class OwnedPointer(BasePointer):
    __slots__ = ('location', 'referenced_type', 'is_mutable')

    def __init__(self, location, referenced_type):
        super().__init__(location, referenced_type, is_mutable=True)


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
    'cvoid': Integer(8, signed=True),
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

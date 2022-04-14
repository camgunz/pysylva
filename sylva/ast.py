# pylint: disable=too-many-lines

import ctypes
import decimal
import typing

from functools import cache, cached_property

from attrs import define, field, resolve_types
from llvmlite import ir # type: ignore

from . import errors, utils
from .location import Location
from .operator import Operator
from .validators import dict_not_empty, list_not_empty, positive


@define(frozen=True)
class ASTNode:
    pass


@define(frozen=True)
class Decl(ASTNode):
    location: Location
    name: str


@define(frozen=True)
class ModuleDecl(Decl):
    pass


@define(frozen=True)
class RequirementDecl(Decl):
    pass


@define(frozen=True)
class SylvaType(ASTNode):

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

    def get_value(self, location: Location, name: str):
        raise NotImplementedError()


@define(frozen=True)
class ParamSylvaType(SylvaType):
    location: Location


@define(frozen=True)
class MetaSylvaType(SylvaType):

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
            if not isinstance(field_type, BasePointerType):
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


@define(frozen=True)
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


@define(frozen=True)
class MetaSylvaLLVMType(MetaSylvaType, SylvaLLVMType):
    pass


@define(frozen=True)
class ScalarType(SylvaLLVMType):
    pass


@define(frozen=True)
class BooleanType(ScalarType):

    @cache
    def get_llvm_type(self, module):
        return ir.IntType(8)

    def get_value(self, location: Location, name: str):
        return BooleanExpr(location, name)


@define(frozen=True)
class RuneType(ScalarType):

    @cache
    def get_llvm_type(self, module):
        return ir.IntType(32)

    def get_value(self, location: Location, name: str):
        return RuneExpr(location, name)


@define(frozen=True)
class NumericType(ScalarType):
    pass


@define(frozen=True)
class SizedNumericType(NumericType):
    bits: int


@define(frozen=True)
class DecimalType(NumericType):

    def get_value(self, location: Location, name: str):
        return DecimalExpr(location, name)


@define(frozen=True)
class ComplexType(SizedNumericType):

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

    def get_value(self, location: Location, name: str):
        return ComplexExpr(location=location, type=self, name=name)


@define(frozen=True)
class FloatType(SizedNumericType):

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

    def get_value(self, location: Location, name: str):
        return FloatValue(location=location, type=self, name=name)


@define(frozen=True)
class IntegerType(SizedNumericType):
    signed: bool

    @classmethod
    def SmallestThatHolds(cls, x):
        return cls(utils.smallest_uint(x), signed=False)

    @cache
    def get_llvm_type(self, module):
        return ir.IntType(self.bits)

    def get_value(self, location: Location, name: str):
        return IntegerValue(location=location, type=self, name=name)


@define(frozen=True)
class StaticStringType(ScalarType):

    @cache
    def get_llvm_type(self, module):
        return ir.PointerType(ir.IntType(8))


@define(frozen=True)
class BaseArrayType(MetaSylvaLLVMType):
    location: Location
    element_type: SylvaType
    element_count: None | int = field(validator=[list_not_empty])

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


@define(frozen=True)
class ArrayType(BaseArrayType):
    pass


@resolve_types
@define(frozen=True)
class EnumType(MetaSylvaLLVMType):
    values: 'typing.Mapping[str, LiteralExpr]' = field(
        validator=[dict_not_empty]
    )

    # pylint: disable=unused-argument
    @values.validator
    def check_empty(self, attribute, value):
        if not len(list(value.keys())):
            raise errors.EmptyEnum(self)

    @cache
    def get_llvm_type(self, module):
        return self.types[0]

    @cached_property
    def names(self):
        return list(self.values.keys()) # pylint: disable=no-member

    @cached_property
    def types(self):
        return list(self.values.values()) # pylint: disable=no-member

    def check(self):
        super().check()

        first_type = self.types[0].type
        for value in self.types[1:]:
            if value.type != first_type:
                raise errors.MismatchedEnumMemberType(first_type, value)


@define(frozen=True)
class BaseFunctionType(MetaSylvaLLVMType):
    parameters: typing.Mapping[str, SylvaType]
    return_type: SylvaType

    @property
    def names(self):
        return list(self.parameters.keys())

    @property
    def types(self):
        return list(self.parameters.values())

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


@define(frozen=True)
class FunctionType(BaseFunctionType):
    pass


@resolve_types
@define(frozen=True)
class InterfaceType(MetaSylvaType):
    fields: 'typing.Mapping[str, FunctionValue | FunctionType]'


@define(frozen=True)
class RangeType(MetaSylvaLLVMType):
    type: NumericType
    min: int
    max: int

    @property
    def names(self):
        return []

    @property
    def types(self):
        return [self.type]

    @cache
    def get_llvm_type(self, module):
        return self.type.type


@define(frozen=True)
class BaseStructType(MetaSylvaLLVMType):
    fields: typing.Mapping[str, SylvaType]

    # self._size = 0
    # self._alignment = 1
    # self._offsets = {}
    # for name, type in self.fields:
    #     self._size = utils.round_up_to_multiple(
    #       self._size, type.alignment
    #     )
    #     self._alignment = max(self._alignment, type.alignment)
    #     self._offsets[name] = self._size
    #     self._size += type.size
    # self._size = utils.round_up_to_multiple(self._size, self._alignment)

    @property
    def names(self):
        return list(self.fields.keys())

    @property
    def types(self):
        return list(self.fields.values())

    def get_field_info(self, name):
        for n, field_name_and_type in enumerate(self.fields.items()):
            field_name, field_type = field_name_and_type
            if field_name == name:
                return n, field_type

    # pylint: disable=arguments-differ
    @cache
    def get_llvm_type(self, module, name=None):
        if name is None:
            for f in self.fields.values():
                if not isinstance(f, BasePointerType):
                    continue
                if not f.referenced_type == self:
                    continue
                raise Exception('Cannot have self-referential struct literals')
            return ir.LiteralStructType([
                f.get_llvm_type(module) for f in self.fields.values()
            ])

        struct = module.get_identified_type(name)
        fields = []
        for f in self.fields.values():
            if not isinstance(f, BasePointerType):
                fields.append(f.get_llvm_type(module))
            elif not f.referenced_type == self:
                fields.append(f.get_llvm_type(module))
            else:
                fields.append(ir.PointerType(struct))
        struct.set_body(*fields)

        return struct


@define(frozen=True)
class StructType(BaseStructType):
    pass


@define(frozen=True)
class ParamStructType(ParamSylvaType):
    type_params: typing.Mapping[str, str | SylvaType]
    fields: typing.Mapping[str, SylvaType]

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
        return StructType(location=location, fields=fields)


@define(frozen=True)
class StringType(StructType):
    location: Location = Location.Generate()
    fields: typing.Mapping[str, SylvaType] = {
        'size': IntegerType( # yapf: disable
            bits=ctypes.sizeof(ctypes.c_size_t * 8),
            signed=False
        ),
        'data': ArrayType(location, IntegerType(8, signed=True), None)
    }

    def get_value(self, location: Location, name: str):
        return StringExpr(location=location, name=name)


@define(frozen=True)
class MetaSylvaLLVMUnionType(MetaSylvaLLVMType):
    fields: typing.Mapping[str, SylvaType]

    @property
    def names(self):
        return list(self.fields.keys())

    @property
    def types(self):
        return list(self.fields.values())

    @cache
    def get_largest_field(self, module):
        fields = list(self.fields.values())
        largest_field = fields[0]
        for f in fields[1:]:
            if f.get_size(module) > largest_field.get_size(module):
                largest_field = f
        return largest_field.get_llvm_type(module)


@define(frozen=True)
class VariantType(MetaSylvaLLVMUnionType):

    def check(self):
        type_errors = super().check()
        type_errors.append(errors.EmptyVariant(self))

        return type_errors

    @cache
    def get_llvm_type(self, module):
        tag_bit_width = utils.round_up_to_multiple(len(self.fields), 8)
        return ir.LiteralStructType([
            self.get_largest_field(module), ir.IntType(tag_bit_width)
        ])


@define(frozen=True)
class ParamVariantType(ParamSylvaType):
    type_params: typing.Mapping[str, str | SylvaType]
    fields: typing.Mapping[str, SylvaType]

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
        return VariantType(location=location, fields=fields)


@define(frozen=True)
class BasePointerType(MetaSylvaLLVMType):
    referenced_type: SylvaType
    is_exclusive: bool

    @property
    def names(self):
        return []

    @property
    def types(self):
        return [self.referenced_type]

    @cache
    def get_llvm_type(self, module):
        return ir.PointerType(self.referenced_type.get_llvm_type(module))


@define(frozen=True)
class ReferencePointerType(BasePointerType):

    def get_value(self, location: Location, name: str):
        return ReferencePointerExpr(location=location, type=self, name=name)


@define(frozen=True)
class OwnedPointerType(BasePointerType):
    is_exclusive: bool = True

    def get_value(self, location: Location, name: str):
        return OwnedPointerExpr(location=location, type=self, name=name)


@define(frozen=True)
class ModuleType(SylvaType):
    value: typing.Any # Module, but we can't because it would be circular

    # pylint: disable=redefined-outer-name
    def lookup(self, location, field):
        return self.value.lookup(location, field)


@define(frozen=True)
class CBitFieldType(SylvaLLVMType):
    bits: int
    signed: bool
    field_size: int

    @cache
    def get_llvm_type(self, module):
        return ir.IntType(self.bits)


@define(frozen=True)
class CVoidType(SylvaLLVMType):

    @cache
    def get_llvm_type(self, module):
        # return ir.VoidType()
        raise Exception('Cannot get the LLVM type of CVoid')


@define(frozen=True)
class CStringType(ScalarType):

    @cache
    def get_llvm_type(self, module):
        return ir.PointerType(ir.IntType(8))


@define(frozen=True)
class CArrayType(BaseArrayType):
    element_count: int = field(validator=[positive])


@define(frozen=True)
class CFunctionType(BaseFunctionType):
    pass


@define(frozen=True)
class CFunctionPointerType(BaseFunctionType):

    def get_llvm_type(self, module):
        return super().get_llvm_type(module).as_pointer()


@define(frozen=True)
class CBlockFunctionType(BaseFunctionType):
    pass


@define(frozen=True)
class CBlockFunctionPointerType(BaseFunctionType):

    def get_llvm_type(self, module):
        return super().get_llvm_type(module).as_pointer()


@define(frozen=True)
class CStructType(BaseStructType):
    pass


@define(frozen=True)
class CUnionType(MetaSylvaLLVMUnionType):

    @cache
    def get_llvm_type(self, module):
        return ir.LiteralStructType([self.get_largest_field(module)])


@define(frozen=True)
class CPtrType(BasePointerType):
    referenced_type_is_exclusive: bool

    def get_value(self, location: Location, name: str):
        return CPointerExpr(location=location, type=self, name=name)


@define(frozen=True)
class Expr(ASTNode):
    location: Location
    type: 'SylvaType'

    # pylint: disable=no-self-use
    def eval(self, location):
        raise errors.ImpossibleCompileTimeEvaluation(location)


@define(frozen=True)
class ValueExpr(Expr):
    name: str | None

    # pylint: disable=unused-argument,no-self-use,redefined-outer-name
    def lookup(self, location, field):
        # raise errors.ImpossibleLookup(location)
        raise errors.ImpossibleCompileTimeEvaluation(location)

    # pylint: disable=unused-argument,no-self-use,redefined-outer-name
    def reflect(self, location, field):
        raise errors.ImpossibleCompileTimeEvaluation(location)
        # if field == 'type':
        #     return self.type
        # if field == 'bytes':
        #     pass
        # raise NotImplementedError()


@define(frozen=True)
class ConstExpr(Expr):
    value: typing.Any

    def eval(self, location):
        return self.value

    # pylint: disable=unused-argument,no-self-use,redefined-outer-name
    def lookup(self, location, field):
        raise NotImplementedError()

        # if isinstance(self.type, types.CStruct):
        #     raise NotImplementedError() # This is a GEP call?
        # if isinstance(self.type, types.CUnion):
        #     raise NotImplementedError() # This is a bitcast and a GEP call?
        # if isinstance(self.type, types.Enum):
        #     raise NotImplementedError() # ???
        # if isinstance(self.type, types.Interface):
        #     raise NotImplementedError() # ???
        # if isinstance(self.type, types.Struct):
        #     raise NotImplementedError() # This is a GEP call?
        # if isinstance(self.type, types.Variant):
        #     raise NotImplementedError() # This is a bitcast and a GEP call?
        # if isinstance(self.type, types.Module):
        #     return self.type.lookup(location, field)

    def reflect(self, location, field):
        if field == 'type':
            return StringLiteralExpr(
                location=location, value=self.type.type_name
            )

        if field == 'bytes':
            pass

        raise NotImplementedError()


@define(frozen=True)
class LiteralExpr(ConstExpr):

    @cache
    def get_llvm_value(self, module):
        return self.type.make_constant(module, self.value)


@define(frozen=True)
class CVoidCastExpr(ConstExpr):
    type: IntegerType = IntegerType(bits=8, signed=True)


@define(frozen=True)
class BooleanLiteralExpr(LiteralExpr):
    type: BooleanType = BooleanType()

    @classmethod
    def FromRawValue(cls, location, raw_value):
        return cls(location, value=raw_value == 'true')

    @cache
    def get_llvm_value(self, module):
        self.type.make_constant(module, 1 if self.value else 0)


@define(frozen=True)
class BooleanExpr(ValueExpr):
    type: BooleanType = BooleanType()


@define(frozen=True)
class RuneLiteralExpr(LiteralExpr):
    type: RuneType = RuneType()

    @classmethod
    def FromRawValue(cls, location, raw_value):
        return cls(location, value=raw_value[1:-1])


@define(frozen=True)
class RuneExpr(ValueExpr):
    type: RuneType = RuneType()


@define(frozen=True)
class StringLiteralExpr(LiteralExpr):
    type: ArrayType

    @classmethod
    def FromRawValue(cls, location, raw_value):
        # [NOTE] I suppose this is where we'd configure internal string
        #        encoding; easy enough to grab from module.program
        encoded_data = bytearray(raw_value[1:-1], encoding='utf-8')
        return cls(
            location,
            type=ArrayType(
                location, IntegerType(8, signed=True), len(encoded_data)
            ),
            value=encoded_data
        )

    # pylint: disable=redefined-outer-name
    def reflect(self, location, field):
        if field == 'size':
            return IntegerLiteralExpr.Platform(
                location,
                signed=False,
                value=len(self.eval(location)),
            )
        if field == 'count':
            # [NOTE] Parameterized decoding is a little harder I guess, but it
            #        doesn't matter for prototype
            return IntegerLiteralExpr.Platform(
                location,
                signed=False,
                value=len(self.eval(location).decode('utf-8'))
            )


@define(frozen=True)
class StringExpr(ValueExpr):
    type: StringType = StringType()

    # pylint: disable=redefined-outer-name
    def reflect(self, location, field):
        if field == 'size':
            field_index, field_type = self.type.get_field_info(field)
            return FieldLookupExpr(location, field_type, self, field_index)

        raise NotImplementedError()


@define(frozen=True)
class NumericLiteralExpr(LiteralExpr):
    pass


@define(frozen=True)
class IntegerLiteralExpr(NumericLiteralExpr):
    type: IntegerType

    @classmethod
    def Build(cls, location, size, signed, value):
        return cls(location, IntegerType(size, signed=signed), value)

    @classmethod
    def Platform(cls, location, signed, value):
        return cls(
            location,
            IntegerType(ctypes.sizeof(ctypes.c_size_t) * 8, signed=signed),
            value
        )

    @classmethod
    def SmallestThatHolds(cls, location, value):
        size = utils.smallest_uint(value)
        return cls.Build(location, size, signed=False, value=value)

    @classmethod
    def FromRawValue(cls, location, raw_value):
        if raw_value.startswith('0b') or raw_value.startswith('0B'):
            base = 2
        elif raw_value.startswith('0o') or raw_value.startswith('0O'):
            base = 8
        elif raw_value.startswith('0x') or raw_value.startswith('0X'):
            base = 16
        else:
            base = 10

        if raw_value.endswith('i'):
            signed, size, value = True, None, int(raw_value[:-1], base)
        elif raw_value.endswith('i8'):
            signed, size, value = True, 8, int(raw_value[:-2], base)
        elif raw_value.endswith('i16'):
            signed, size, value = True, 16, int(raw_value[:-3], base)
        elif raw_value.endswith('i32'):
            signed, size, value = True, 32, int(raw_value[:-3], base)
        elif raw_value.endswith('i64'):
            signed, size, value = True, 64, int(raw_value[:-3], base)
        elif raw_value.endswith('i128'):
            signed, size, value = True, 128, int(raw_value[:-4], base)
        elif raw_value.endswith('u'):
            signed, size, value = False, None, int(raw_value[:-1], base)
        elif raw_value.endswith('u8'):
            signed, size, value = False, 8, int(raw_value[:-2], base)
        elif raw_value.endswith('u16'):
            signed, size, value = False, 16, int(raw_value[:-3], base)
        elif raw_value.endswith('u32'):
            signed, size, value = False, 32, int(raw_value[:-3], base)
        elif raw_value.endswith('u64'):
            signed, size, value = False, 64, int(raw_value[:-3], base)
        elif raw_value.endswith('u128'):
            signed, size, value = False, 128, int(raw_value[:-4], base)
        else: # [NOTE] Warn here?
            signed, size = False, None

        size = size or ctypes.sizeof(ctypes.c_size_t) * 8

        return cls.Build(location, size, signed, value)

    @property
    def signed(self):
        return self.type.signed

    @property
    def size(self):
        return self.type.bits

    @property
    def type_name(self):
        return f'{"i" if self.signed else "u"}{self.size}'


@define(frozen=True)
class IntegerValue(ValueExpr):
    type: IntegerType

    @classmethod
    def Build(cls, location: Location, size: int, signed: bool, name: str):
        return cls(location, type=IntegerType(size, signed=signed), name=name)


@define(frozen=True)
class FloatLiteralExpr(NumericLiteralExpr):
    type: FloatType

    @classmethod
    def Build(cls, location, size, value):
        super().__init__(location, FloatType(size), value)

    @classmethod
    def FromRawValue(cls, location, raw_value):
        if raw_value.endswith('f16'):
            return cls(location, FloatType(16), float(raw_value[:-3]))
        if raw_value.endswith('f32'):
            return cls(location, FloatType(32), float(raw_value[:-3]))
        if raw_value.endswith('f64'):
            return cls(location, FloatType(64), float(raw_value[:-3]))
        if raw_value.endswith('f128'):
            return cls(location, FloatType(128), float(raw_value[:-4]))
        raise Exception(f'Malformed float value {raw_value}')

    @property
    def size(self):
        return self.type.bits


@define(frozen=True)
class FloatValue(ValueExpr):
    type: FloatType

    @classmethod
    def Build(cls, location: Location, size: int, name: str):
        cls(location, type=FloatType(size), name=name)


@define(frozen=True)
class ComplexLiteralExpr(NumericLiteralExpr):
    type: ComplexType

    @classmethod
    def Build(cls, location, size, value):
        super().__init__(location, ComplexType(size), value)

    @classmethod
    def FromRawValue(cls, location, raw_value):
        if raw_value.endswith('f16'):
            return cls(location, ComplexType(16), complex(raw_value[:-3]))
        if raw_value.endswith('f32'):
            return cls(location, ComplexType(32), complex(raw_value[:-3]))
        if raw_value.endswith('f64'):
            return cls(location, ComplexType(64), complex(raw_value[:-3]))
        if raw_value.endswith('f128'):
            return cls(location, ComplexType(128), complex(raw_value[:-4]))
        raise Exception(f'Malformed complex value {raw_value}')

    @property
    def size(self):
        return self.type.bits


@define(frozen=True)
class ComplexExpr(ValueExpr):
    type: ComplexType

    @classmethod
    def Build(cls, location: Location, size: int, name: str):
        cls(location, type=ComplexType(size), name=name)


@define(frozen=True)
class DecimalLiteralExpr(NumericLiteralExpr):
    type: DecimalType = DecimalType()

    @classmethod
    def FromRawValue(cls, location, raw_value):
        return cls(location, value=decimal.Decimal(raw_value))


@define(frozen=True)
class DecimalExpr(ValueExpr):
    type: DecimalType = DecimalType()


@define(frozen=True)
class FunctionValue(ValueExpr):
    type: FunctionType


@define(frozen=True)
class CallExpr(Expr):
    function: Expr
    arguments: list[Expr]


@define(frozen=True)
class IndexExpr(Expr):
    indexable: Expr
    index: Expr


@define(frozen=True)
class UnaryExpr(Expr):
    operator: Operator
    expr: Expr


@define(frozen=True)
class BinaryExpr(Expr):
    operator: Operator
    lhs: Expr
    rhs: Expr


@define(frozen=True)
class FieldLookupExpr(Expr):
    object: Expr
    index: int


@define(frozen=True)
class MoveExpr(ConstExpr):
    type: OwnedPointerType
    value: Expr


@define(frozen=True)
class BasePointerExpr(ValueExpr):

    @property
    def referenced_type(self):
        return self.type.referenced_type

    @property
    def is_exclusive(self):
        return self.type.is_exclusive

    def deref(self, location, name):
        return self.referenced_type.get_value(location, name)


class ReferencePointerExpr(BasePointerExpr):
    type: ReferencePointerType

    @classmethod
    def Build(cls, location, referenced_type, is_exclusive, name):
        return cls(
            location,
            ReferencePointerType(location, referenced_type, is_exclusive),
            name
        )


@define(frozen=True)
class OwnedPointerExpr(BasePointerExpr):
    type: OwnedPointerType


@define(frozen=True)
class CPointerExpr(BasePointerExpr):
    type: CPtrType

    @classmethod
    def Build(
        cls,
        location,
        referenced_type,
        referenced_type_is_exclusive,
        is_exclusive,
        name
    ):
        return cls(
            location,
            CPtrType(
                location,
                referenced_type,
                referenced_type_is_exclusive,
                is_exclusive
            ),
            name
        )


@define(frozen=True)
class Stmt(ASTNode):
    location: Location


@define(frozen=True)
class StmtBlock(Stmt):
    code: list[Expr | Stmt]


@define(frozen=True)
class Break(Stmt):
    pass


@define(frozen=True)
class Continue(Stmt):
    pass


@define(frozen=True)
class Return(Stmt):
    expr: Expr


@define(frozen=True)
class If(StmtBlock):
    conditional_expr: Expr
    else_code: list[Expr | Stmt]


@define(frozen=True)
class Loop(StmtBlock):
    pass


@define(frozen=True)
class While(StmtBlock):
    conditional_expr: Expr


@define(frozen=True)
class Def(ASTNode):
    location: Location
    module: typing.Any
    name: str
    value: ConstExpr | SylvaType


@define(frozen=True)
class ConstDef(Def):
    value: ConstExpr


@define(frozen=True)
class TypeDef(Def):
    value: SylvaType


@define(frozen=True)
class FunctionDef(TypeDef):
    value: FunctionType
    code: list[Expr | Stmt]


@define(frozen=True)
class CFunctionDef(TypeDef):
    value: CFunctionType


@define(frozen=True)
class CUnionDef(TypeDef):
    value: CUnionType


@define(frozen=True)
class CStructDef(TypeDef):
    value: CStructType


@define(frozen=True)
class DeferredTypeLookup:
    location: Location
    value: str


@define(frozen=True)
class Implementation(ASTNode):
    location: Location
    interface: InterfaceType
    implementing_type: SylvaType
    funcs: list[FunctionValue]


BUILTIN_TYPES = {
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
    'cvoid': IntegerType(8, signed=True),
    'bool': BooleanType(),
    'c16': ComplexType(16),
    'c32': ComplexType(32),
    'c64': ComplexType(64),
    'c128': ComplexType(128),
    'cstr': CStringType(),
    'dec': DecimalType(),
    'f16': FloatType(16),
    'f32': FloatType(32),
    'f64': FloatType(64),
    'f128': FloatType(128),
    'int': IntegerType(ctypes.sizeof(ctypes.c_size_t) * 8, signed=True),
    'i8': IntegerType(8, signed=True),
    'i16': IntegerType(16, signed=True),
    'i32': IntegerType(32, signed=True),
    'i64': IntegerType(64, signed=True),
    'i128': IntegerType(128, signed=True),
    'rune': RuneType(),
    'str': StringType(),
    'uint': IntegerType(ctypes.sizeof(ctypes.c_size_t) * 8, signed=False),
    'u8': IntegerType(8, signed=False),
    'u16': IntegerType(16, signed=False),
    'u32': IntegerType(32, signed=False),
    'u64': IntegerType(64, signed=False),
    'u128': IntegerType(128, signed=False),
}

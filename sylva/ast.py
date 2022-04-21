# pylint: disable=too-many-lines

import ctypes
import decimal
import typing

from functools import cache, cached_property

from attrs import define, field
from llvmlite import ir # type: ignore

from . import errors, utils
from .location import Location
from .operator import Operator


_SIZE_SIZE = ctypes.sizeof(ctypes.c_size_t) * 8


@define(eq=False, slots=True)
class ASTNode:
    location: Location


@define(eq=False, slots=True)
class Decl(ASTNode):
    name: str


@define(eq=False, slots=True)
class ModuleDecl(Decl):
    pass


@define(eq=False, slots=True)
class RequirementDecl(Decl):
    pass


@define(eq=False, slots=True)
class SylvaType(ASTNode):

    # pylint: disable=no-self-use
    def check(self):
        return []

    def get_value(self, location: Location, name: str):
        raise NotImplementedError()


@define(eq=False, slots=True)
class ParamSylvaType(SylvaType):
    pass


@define(eq=False, slots=True)
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


@define(eq=False, slots=True)
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


@define(eq=False, slots=True)
class MetaSylvaLLVMType(MetaSylvaType, SylvaLLVMType):
    pass


@define(eq=False, slots=True)
class ScalarType(SylvaLLVMType):
    pass


@define(eq=False, slots=True)
class BooleanType(ScalarType):

    @cache
    def get_llvm_type(self, module):
        return ir.IntType(8)

    def get_value(self, location: Location, name: str):
        return BooleanExpr(location, name)


@define(eq=False, slots=True)
class RuneType(ScalarType):

    @cache
    def get_llvm_type(self, module):
        return ir.IntType(32)

    def get_value(self, location: Location, name: str):
        return RuneExpr(location, name)


@define(eq=False, slots=True)
class NumericType(ScalarType):
    pass


@define(eq=False, slots=True)
class SizedNumericType(NumericType):
    bits: int


@define(eq=False, slots=True)
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


@define(eq=False, slots=True)
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
        return FloatExpr(location=location, type=self, name=name)


@define(eq=False, slots=True)
class IntegerType(SizedNumericType):
    signed: bool

    @classmethod
    def SmallestThatHolds(cls, x):
        return cls(utils.smallest_uint(x), signed=False)

    @classmethod
    def Platform(cls, signed):
        return cls(bits=_SIZE_SIZE, signed=signed)

    @cache
    def get_llvm_type(self, module):
        return ir.IntType(self.bits)

    def get_value(self, location: Location, name: str):
        return IntegerExpr(location=location, type=self, name=name)


@define(eq=False, slots=True)
class StaticStringType(ScalarType):

    @cache
    def get_llvm_type(self, module):
        return ir.PointerType(ir.IntType(8))


@define(eq=False, slots=True)
class BaseArrayType(MetaSylvaLLVMType):
    element_type: SylvaType
    element_count: None | int = field()

    # pylint: disable=unused-argument
    @element_count.validator
    def check_element_count(self, attribute, value):
        if value is not None and value <= 0:
            raise errors.EmptyArray(self.location)

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

    # pylint: disable=no-self-use,redefined-outer-name
    @cache
    def get_reflection_field_info(self, field):
        if field == 'size':
            return IntegerType.Platform(signed=False)
        if field == 'count':
            return IntegerType.Platform(signed=False)


@define(eq=False, slots=True)
class ArrayType(BaseArrayType):
    pass


@define(eq=False, slots=True)
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


@define(eq=False, slots=True)
class FunctionType(BaseFunctionType):
    pass


@define(eq=False, slots=True)
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


@define(eq=False, slots=True)
class BaseStructType(MetaSylvaLLVMType):
    name: str | None
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

    @cache
    def get_field_info(self, name):
        for n, field_name_and_type in enumerate(self.fields.items()):
            field_name, field_type = field_name_and_type
            if field_name == name:
                return n, field_type

    # pylint: disable=arguments-differ
    @cache
    def get_llvm_type(self, module):
        if self.name is None:
            for f in self.fields.values():
                if not isinstance(f, BasePointerType):
                    continue
                if not f.referenced_type == self:
                    continue
                raise Exception('Cannot have self-referential struct literals')
            return ir.LiteralStructType([
                f.get_llvm_type(module) for f in self.fields.values()
            ])

        struct = module.get_identified_type(self.name)
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


@define(eq=False, slots=True)
class StructType(BaseStructType):
    pass


@define(eq=False, slots=True)
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


@define(eq=False, slots=True)
class StringType(StructType):
    fields: typing.Mapping[str, SylvaType] = {
        'size': IntegerType( # yapf: disable
            location=Location.Generate(), bits=_SIZE_SIZE, signed=False
        ),
        'data': ArrayType( # yapf: disable
            Location.Generate(),
            IntegerType(Location.Generate(), 8, signed=True),
            None
        )
    }

    def get_value(self, location: Location, name: str):
        return StringExpr(location=location, name=name)

    # pylint: disable=no-self-use,redefined-outer-name
    @cache
    def get_reflection_field_info(self, field):
        if field == 'size':
            return IntegerType.Platform(signed=False)
        if field == 'count':
            return IntegerType.Platform(signed=False)


@define(eq=False, slots=True)
class BaseUnionType(MetaSylvaLLVMType):
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

    @cache
    def get_field_info(self, name):
        for n, field_name_and_type in enumerate(self.fields.items()):
            field_name, field_type = field_name_and_type
            if field_name == name:
                return n, field_type


@define(eq=False, slots=True)
class VariantType(BaseUnionType):

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


@define(eq=False, slots=True)
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


@define(eq=False, slots=True)
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

    # pylint: disable=redefined-outer-name
    @cache
    def get_reflection_field_info(self, field):
        return self.referenced_type.get_reflection_field_info(field)


@define(eq=False, slots=True)
class ReferencePointerType(BasePointerType):

    def get_value(self, location: Location, name: str):
        return ReferencePointerExpr(location=location, type=self, name=name)


@define(eq=False, slots=True)
class OwnedPointerType(BasePointerType):
    is_exclusive: bool = True

    def get_value(self, location: Location, name: str):
        return OwnedPointerExpr(location=location, type=self, name=name)


@define(eq=False, slots=True)
class CPointerType(BasePointerType):
    referenced_type_is_exclusive: bool

    def get_value(self, location: Location, name: str):
        return CPointerCastExpr(location=location, type=self, name=name)


@define(eq=False, slots=True)
class ModuleType(SylvaType):
    value: typing.Any # Module, but we can't because it would be circular


@define(eq=False, slots=True)
class CBitFieldType(SylvaLLVMType):
    bits: int
    signed: bool
    field_size: int

    @cache
    def get_llvm_type(self, module):
        return ir.IntType(self.bits)


@define(eq=False, slots=True)
class CVoidType(SylvaLLVMType):

    @cache
    def get_llvm_type(self, module):
        # return ir.VoidType()
        raise Exception('Cannot get the LLVM type of CVoid')


@define(eq=False, slots=True)
class CStringType(ScalarType):

    @cache
    def get_llvm_type(self, module):
        return ir.PointerType(ir.IntType(8))


@define(eq=False, slots=True)
class CArrayType(BaseArrayType):
    element_count: int | None = field()


@define(eq=False, slots=True)
class CFunctionType(BaseFunctionType):
    pass


@define(eq=False, slots=True)
class CFunctionPointerType(BaseFunctionType):

    def get_llvm_type(self, module):
        return super().get_llvm_type(module).as_pointer()


@define(eq=False, slots=True)
class CBlockFunctionType(BaseFunctionType):
    pass


@define(eq=False, slots=True)
class CBlockFunctionPointerType(BaseFunctionType):

    def get_llvm_type(self, module):
        return super().get_llvm_type(module).as_pointer()


@define(eq=False, slots=True)
class CStructType(BaseStructType):
    pass


@define(eq=False, slots=True)
class CUnionType(BaseUnionType):

    @cache
    def get_llvm_type(self, module):
        return ir.LiteralStructType([self.get_largest_field(module)])


@define(eq=False, slots=True)
class Expr(ASTNode):
    type: SylvaType

    # pylint: disable=no-self-use
    def eval(self, scope):
        raise errors.ImpossibleCompileTimeEvaluation(self.location)


@define(eq=False, slots=True)
class ValueExpr(Expr):
    pass


@define(eq=False, slots=True)
class ConstExpr(Expr):

    # pylint: disable=unused-argument,no-self-use,redefined-outer-name
    def lookup(self, location, field):
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
        raise NotImplementedError()

    def reflect(self, location, field):
        # if field == 'type':
        #     pass
        # if field == 'bytes':
        #     pass
        raise NotImplementedError()


@define(eq=False, slots=True)
class LiteralExpr(ConstExpr):
    value: typing.Any

    def eval(self, scope):
        return self.value

    @cache
    def get_llvm_value(self, module):
        return self.type.make_constant(module, self.value)


@define(eq=False, slots=True)
class CVoidCastExpr(ConstExpr):
    expr: Expr
    type: IntegerType = IntegerType(Location.Generate(), bits=8, signed=True)


@define(eq=False, slots=True)
class BooleanLiteralExpr(LiteralExpr):
    type: BooleanType = BooleanType(Location.Generate())

    @classmethod
    def FromRawValue(cls, location, raw_value):
        return cls(location, value=raw_value == 'true')

    @cache
    def get_llvm_value(self, module):
        self.type.make_constant(module, 1 if self.value else 0)


@define(eq=False, slots=True)
class BooleanExpr(ValueExpr):
    type: BooleanType = BooleanType(Location.Generate())


@define(eq=False, slots=True)
class RuneLiteralExpr(LiteralExpr):
    type: RuneType = RuneType(Location.Generate())

    @classmethod
    def FromRawValue(cls, location, raw_value):
        return cls(location, value=raw_value[1:-1])


@define(eq=False, slots=True)
class RuneExpr(ValueExpr):
    type: RuneType = RuneType(Location.Generate())


@define(eq=False, slots=True)
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
                location=location,
                element_type=IntegerType(
                    Location.Generate(), bits=8, signed=True
                ),
                element_count=len(encoded_data)
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


@define(eq=False, slots=True)
class StringExpr(ValueExpr):
    type: StringType = StringType(Location.Generate(), name='str')

    # pylint: disable=redefined-outer-name
    def reflect(self, location, field):
        if field == 'size':
            field_index, field_type = self.type.get_field_info(field)
            return FieldIndexLookupExpr(
                location, field_type, self, field_index
            )

        raise NotImplementedError()


@define(eq=False, slots=True)
class NumericLiteralExpr(LiteralExpr):
    pass


@define(eq=False, slots=True)
class IntegerLiteralExpr(NumericLiteralExpr):
    type: IntegerType

    @classmethod
    def Platform(cls, location, signed, value):
        return cls(location, IntegerType(_SIZE_SIZE, signed=signed), value)

    @classmethod
    def SmallestThatHolds(cls, location, value):
        type = IntegerType(size=utils.smallest_uint(value), signed=False)
        return cls(location=location, type=type, value=value)

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

        return cls(
            location=location,
            type=IntegerType(
                location=location, bits=size or _SIZE_SIZE, signed=signed
            ),
            value=value
        )

    @property
    def signed(self):
        return self.type.signed

    @property
    def size(self):
        return self.type.bits


@define(eq=False, slots=True)
class IntegerExpr(ValueExpr):
    type: IntegerType


@define(eq=False, slots=True)
class FloatLiteralExpr(NumericLiteralExpr):
    type: FloatType

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


@define(eq=False, slots=True)
class FloatExpr(ValueExpr):
    type: FloatType


@define(eq=False, slots=True)
class ComplexLiteralExpr(NumericLiteralExpr):
    type: ComplexType

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


@define(eq=False, slots=True)
class ComplexExpr(ValueExpr):
    type: ComplexType


@define(eq=False, slots=True)
class LookupExpr(ConstExpr):
    name: str

    def eval(self, scope):
        value = scope.lookup(self.name)
        if value is None:
            raise errors.UndefinedSymbol(self.location, self.name)
        return value


@define(eq=False, slots=True)
class LLVMExpr(Expr):

    def eval(self, scope, builder, name=None):
        raise NotImplementedError()


@define(eq=False, slots=True)
class FieldNameLookupExpr(LLVMExpr):
    expr: Expr
    name: str


@define(eq=False, slots=True)
class FieldIndexLookupExpr(LLVMExpr):
    expr: Expr
    index: int

    def emit(self, builder, name=None):
        indices = [self.index]
        expr = self.expr # struct, cstruct... array?
        while isinstance(expr, FieldIndexLookupExpr):
            expr = expr.expr
            indices.insert(0, expr.index)

        return builder.gep(
            self.expr.eval(scope), indices, inbounds=True, name=name
        )


@define(eq=False, slots=True)
class ReflectionLookupExpr(Expr):
    expr: Expr
    name: str


@define(eq=False, slots=True)
class FunctionExpr(ValueExpr):
    type: FunctionType


@define(eq=False, slots=True)
class CallExpr(Expr):
    function: Expr
    arguments: list[Expr]


@define(eq=False, slots=True)
class IndexExpr(Expr):
    indexable: Expr
    index: Expr


@define(eq=False, slots=True)
class UnaryExpr(Expr):
    operator: Operator
    expr: Expr


@define(eq=False, slots=True)
class BinaryExpr(Expr):
    operator: Operator
    lhs: Expr
    rhs: Expr


@define(eq=False, slots=True)
class BasePointerExpr(ValueExpr):

    @property
    def referenced_type(self):
        return self.type.referenced_type

    @property
    def is_exclusive(self):
        return self.type.is_exclusive


@define(eq=False, slots=True)
class ReferencePointerExpr(BasePointerExpr):
    type: ReferencePointerType
    value: Expr


@define(eq=False, slots=True)
class MovePointerExpr(ConstExpr):
    type: OwnedPointerType
    value: Expr


@define(eq=False, slots=True)
class OwnedPointerExpr(BasePointerExpr):
    type: OwnedPointerType


@define(eq=False, slots=True)
class CPointerCastExpr(BasePointerExpr):

    """
    "Cast" is a misnomer here because while this casts other pointer
    types, it takes a (c) pointer to non-pointer types.
    """

    type: CPointerType
    expr: Expr


@define(eq=False, slots=True)
class Stmt(ASTNode):
    pass


@define(eq=False, slots=True)
class StmtBlock(Stmt):
    code: list[Expr | Stmt]


@define(eq=False, slots=True)
class Break(Stmt):
    pass


@define(eq=False, slots=True)
class Continue(Stmt):
    pass


@define(eq=False, slots=True)
class Return(Stmt):
    expr: Expr


@define(eq=False, slots=True)
class If(StmtBlock):
    conditional_expr: Expr
    else_code: list[Expr | Stmt]


@define(eq=False, slots=True)
class Loop(StmtBlock):
    pass


@define(eq=False, slots=True)
class While(StmtBlock):
    conditional_expr: Expr


@define(eq=False, slots=True)
class BaseTypeMapping(ASTNode):
    name: str
    type: SylvaType


@define(eq=False, slots=True)
class Parameter(BaseTypeMapping):
    pass


@define(eq=False, slots=True)
class Field(BaseTypeMapping):
    index: int


@define(eq=False, slots=True)
class Def(ASTNode):
    name: str


@define(eq=False, slots=True)
class AliasDef(Def):
    value: str | SylvaType = field()

    # pylint: disable=unused-argument
    @value.validator
    def check_value(self, attribute, value):
        if isinstance(value, str) and value == self.name:
            raise errors.RedundantAlias(self.location, self.name)


@define(eq=False, slots=True)
class ConstDef(Def):
    value: ConstExpr


@define(eq=False, slots=True)
class FunctionDef(Def):
    type: FunctionType
    code: list[Expr | Stmt]


@define(eq=False, slots=True)
class CFunctionDef(Def):
    type: CFunctionType


@define(eq=False, slots=True)
class TypeDef(Def):
    type: SylvaType


@define(eq=False, slots=True)
class IndexedFieldsTypeDef(TypeDef):
    type: StructType | CStructType | ArrayType | CArrayType

    # pylint: disable=unused-argument,no-self-use,redefined-outer-name
    def lookup(self, location: Location, field: str):
        field_index, field_type = self.type.get_field_info(field)
        return FieldIndexLookupExpr(location, field_type, self, field_index)

    # pylint: disable=unused-argument,no-self-use,redefined-outer-name
    # def reflect(self, location, field):
    #     return self.value.reflect(location, field)


@define(eq=False, slots=True)
class CArrayDef(IndexedFieldsTypeDef):
    pass


@define(eq=False, slots=True)
class StructDef(IndexedFieldsTypeDef):
    pass


@define(eq=False, slots=True)
class CStructDef(IndexedFieldsTypeDef):
    pass


@define(eq=False, slots=True)
class DeferredTypeLookup(ASTNode):
    value: str


@define(eq=False, slots=True)
class InterfaceType(MetaSylvaType):
    fields: typing.Mapping[str, FunctionExpr | FunctionType]

    @cache
    def get_field_info(self, name):
        for n, field_name_and_value in enumerate(self.fields.items()):
            field_name, field_value = field_name_and_value
            if field_name == name:
                return n, field_value


@define(eq=False, slots=True)
class Implementation(ASTNode):
    interface: InterfaceType
    implementing_type: SylvaType
    funcs: list[FunctionExpr]


@define(eq=False, slots=True)
class EnumType(MetaSylvaLLVMType):
    # yapf: disable
    values: typing.Mapping[
        str,
        LiteralExpr
    ] = field()

    # pylint: disable=unused-argument
    @values.validator
    def check_values(self, attribute, value):
        if len(list(value.keys())) <= 0:
            raise errors.EmptyEnum(self.location)

    @cache
    def get_llvm_type(self, module):
        return self.types[0].get_llvm_type(module)

    @cache
    def get_field_info(self, name):
        vals = self.values.items() # pylint: disable=no-member
        for n, field_name_and_value in enumerate(vals):
            field_name, field_value = field_name_and_value
            if field_name == name:
                return n, field_value

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


@define(eq=False, slots=True)
class NamedFieldsTypeDef(TypeDef):
    type: VariantType | CUnionType | EnumType | InterfaceType

    # pylint: disable=unused-argument,no-self-use,redefined-outer-name
    def lookup(self, location: Location, field: str):
        _, field_type = self.type.get_field_info(field)
        return FieldNameLookupExpr(location, field_type, self, field)

    # pylint: disable=unused-argument,no-self-use,redefined-outer-name
    # def reflect(self, location, field):
    #     return self.value.reflect(location, field)


@define(eq=False, slots=True)
class VariantDef(NamedFieldsTypeDef):
    pass


@define(eq=False, slots=True)
class CUnionDef(NamedFieldsTypeDef):
    pass


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
    # 'cptr': CPointer(), # meta
    'cvoid': IntegerType(Location.Generate(), 8, signed=True),
    'bool': BooleanType(Location.Generate()),
    'c16': ComplexType(Location.Generate(), 16),
    'c32': ComplexType(Location.Generate(), 32),
    'c64': ComplexType(Location.Generate(), 64),
    'c128': ComplexType(Location.Generate(), 128),
    'cstr': CStringType(Location.Generate()),
    'f16': FloatType(Location.Generate(), 16),
    'f32': FloatType(Location.Generate(), 32),
    'f64': FloatType(Location.Generate(), 64),
    'f128': FloatType(Location.Generate(), 128),
    'int': IntegerType(Location.Generate(), _SIZE_SIZE, signed=True),
    'i8': IntegerType(Location.Generate(), 8, signed=True),
    'i16': IntegerType(Location.Generate(), 16, signed=True),
    'i32': IntegerType(Location.Generate(), 32, signed=True),
    'i64': IntegerType(Location.Generate(), 64, signed=True),
    'i128': IntegerType(Location.Generate(), 128, signed=True),
    'rune': RuneType(Location.Generate()),
    'str': StringType(Location.Generate(), name='str'),
    'uint': IntegerType(Location.Generate(), _SIZE_SIZE, signed=False),
    'u8': IntegerType(Location.Generate(), 8, signed=False),
    'u16': IntegerType(Location.Generate(), 16, signed=False),
    'u32': IntegerType(Location.Generate(), 32, signed=False),
    'u64': IntegerType(Location.Generate(), 64, signed=False),
    'u128': IntegerType(Location.Generate(), 128, signed=False),
}

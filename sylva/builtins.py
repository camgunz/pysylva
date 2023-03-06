import enum
import itertools

from dataclasses import dataclass, field
from functools import cached_property
from typing import Any, Optional, Union

from sylva import _SIZE_SIZE, errors, utils
from sylva.location import Location


class TypeModifier(enum.Enum):
    NoMod = enum.auto()
    Ptr = enum.auto()
    Ref = enum.auto()
    ExRef = enum.auto()
    CMut = enum.auto()


@dataclass(kw_only=True)
class SylvaObject:
    location: Location = field(default_factory=Location.Generate)


@dataclass(kw_only=True)
class SylvaType(SylvaObject):
    mod: TypeModifier = TypeModifier.NoMod

    @cached_property
    def mname(self):
        raise NotImplementedError()


@dataclass(kw_only=True)
class SylvaValue(SylvaObject):
    type: SylvaType
    value: Any


@dataclass(kw_only=True)
class SylvaField(SylvaObject):
    name: str
    type: Optional[SylvaType]

    @property
    def is_var(self):
        return (
            self.type is None or
            (hasattr(self.type, 'is_var') and self.type.is_var)
        )


@dataclass(kw_only=True)
class SylvaDef(SylvaObject):
    name: str
    value: SylvaValue

    @property
    def type(self):
        return self.value.type


# @dataclass(kw_only=True)
# class CMutType(SylvaType):
#     mod: TypeModifier = field(init=False, default=TypeModifier.CMut)
#     referenced_type: SylvaType
#
#
# @dataclass(kw_only=True)
# class PtrType(SylvaType):
#     mod: TypeModifier = field(init=False, default=TypeModifier.Ptr)
#     referenced_type: SylvaType
#
#
# @dataclass(kw_only=True)
# class RefType(SylvaType):
#     mod: TypeModifier = field(init=False, default=TypeModifier.Ref)
#     referenced_type: SylvaType
#
#
# @dataclass(kw_only=True)
# class ExRefType(SylvaType):
#     mod: TypeModifier = field(init=False, default=TypeModifier.ExRef)
#     referenced_type: SylvaType


@dataclass(kw_only=True)
class BoolType(SylvaType):

    @cached_property
    def mname(self):
        return '4bool'


@dataclass(kw_only=True)
class BoolValue(SylvaValue):
    type: BoolType
    value: bool


@dataclass(kw_only=True)
class MonoCPtrType(SylvaType):
    referenced_type: SylvaType

    @cached_property
    def mname(self):
        ref_ex = 'x' if self.referenced_type_is_exclusive else 's'
        return ''.join([f'3cp{ref_ex}', self.referenced_type.mname])

    @cached_property
    def referenced_type_is_exclusive(self) -> bool:
        return self.referenced_type.mod in (
            TypeModifier.CMut,
            TypeModifier.ExRef,
            TypeModifier.Ptr,
        )


@dataclass(kw_only=True)
class ParamCPtrType(SylvaType):

    @property
    def is_var(self):
        return True

    def get_monomorphization(
        self,
        location: Location,
        referenced_type: SylvaType,
    ) -> MonoCPtrType:
        return MonoCPtrType(location, referenced_type)


@dataclass(kw_only=True)
class CPtrType(SylvaType):

    @staticmethod
    def build_type(
        location: Location,
        mod: TypeModifier = TypeModifier.NoMod,
        referenced_type: Optional[SylvaType] = None,
    ) -> Union[MonoCPtrType, ParamCPtrType]:
        return (
            MonoCPtrType(
                location=location,
                mod=mod,
                referenced_type=referenced_type,
            ) if referenced_type is not None else ParamCPtrType(location)
        )


@dataclass(kw_only=True)
class CPtrValue(SylvaValue):
    type: MonoCPtrType


@dataclass(kw_only=True)
class CStrType(SylvaType):

    @cached_property
    def mname(self):
        return '4cstr'


@dataclass(kw_only=True)
class CStrValue(SylvaValue):
    type: CStrType
    value: str


@dataclass(kw_only=True)
class CVoidType(SylvaType):
    name: str = field(init=False, default='cvoid')
    is_exclusive: bool = False

    @cached_property
    def mname(self):
        return '5cvoid'


@dataclass(kw_only=True)
class CVoidValue(SylvaValue):
    type: CVoidType
    value: None = None


@dataclass(kw_only=True)
class MonoEnumType(SylvaType):
    values: dict[str, SylvaValue]

    def __post_init__(self):
        if len(self.values) <= 0:
            raise errors.EmptyEnum(self.location)

        dupes = utils.get_dupes(self.values.keys())
        if dupes:
            raise errors.DuplicateFields(self, dupes)

        if any(v.type != self.type for v in list(self.values.values())[1:]):
            raise errors.InconsistentEnumMemberTypes(self)

    def get_attribute(self, name):
        return self.values.get(name)

    @cached_property
    def mname(self):
        return ''.join(['1e', self.values[0].type.mname])

    @cached_property
    def type(self):
        return next(self.values.items()).type


@dataclass(kw_only=True)
class EnumType(SylvaType):

    @staticmethod
    def build_type(
        location: Location,
        values: dict[str, SylvaValue],
        mod: TypeModifier = TypeModifier.NoMod,
    ) -> MonoEnumType:
        return MonoEnumType(location=location, values=values)


@dataclass(kw_only=True)
class EnumValue(SylvaValue):
    type: MonoEnumType


@dataclass(kw_only=True)
class MonoFnType(SylvaType):
    parameters: list[SylvaField] = field(default_factory=list)
    return_type: Optional[SylvaType]

    def __post_init__(self):
        if dupes := utils.get_dupes(p.name for p in self.parameters):
            raise errors.DuplicateParameters(self, dupes)

    @cached_property
    def mname(self):
        return ''.join([
            '2fn',
            ''.join(p.type.mname for p in self.parameters),
            self.return_type.mname if self.return_type else '1v'
        ])


@dataclass(kw_only=True)
class MonoCFnType(SylvaType):
    parameters: list[SylvaField] = field(default_factory=list)
    return_type: Optional[SylvaType]

    def __post_init__(self):
        if dupes := utils.get_dupes(p.name for p in self.parameters):
            raise errors.DuplicateParameters(self, dupes)

    @cached_property
    def mname(self):
        return ''.join([
            '3cfn',
            ''.join(p.type.mname for p in self.parameters),
            self.return_type.mname if self.return_type else '1v'
        ])


@dataclass(kw_only=True)
class ParamFnType(SylvaType):
    return_type_param: Optional[SylvaField] = field(default=None)

    @property
    def return_type_is_type_parameter(self):
        return (
            self.return_type_param and self.return_type_param.is_type_parameter
        )

    @property
    def return_type(self):
        return (
            None if not self.return_type_param else self.return_type_param.type
        )

    @property
    def return_type_param_name(self):
        return (
            None if not self.return_type_param else self.return_type_param.name
        )

    @property
    def type_parameters(self):
        return ([p.name for p in self.parameters if p.is_var] +
                ([self.return_type]
                 if self.return_type_is_type_parameter else []))

    @property
    def return_type_must_be_inferred(self):
        return (
            self.return_type_is_type_parameter and self.return_type_param.name
            not in [p.name for p in self.type_parameters]
        )

    def get_monomorphization(
        self,
        location: Location,
        parameters: list[SylvaField],
        return_type: Optional[SylvaType],
    ) -> MonoFnType:
        if self.return_type_must_be_inferred and return_type is None:
            raise errors.InvalidParameterization(
                location,
                'Cannot parameterize function return type; return type could '
                'not be inferred, and its type parameter '
                f'"{self.return_type_param_name}" was not found in function '
                'parameters'
            )

        if len(parameters) != len(self.parameters):
            raise errors.InvalidParameterization(
                location,
                f'Expected {len(self.parameters)} parameters, got '
                f'{len(parameters)}'
            )

        iparams = iter(parameters)

        return MonoFnType(
            location=location,
            parameters=[
                p if not p.is_var else next(iparams) for p in self.parameters
            ],
            return_type=return_type
        )


@dataclass(kw_only=True)
class FnType(SylvaType):

    @staticmethod
    def build_type(
        location: Location,
        mod: TypeModifier = TypeModifier.NoMod,
        parameters: list[SylvaField] = field(default_factory=list),
        return_type: Optional[SylvaType] = None,
    ) -> Union[MonoFnType, ParamFnType]:
        return (
            ParamFnType(
                location=location,
                parameters=parameters,
                return_type=return_type
            ) if any(p.is_var for p in parameters) else MonoFnType(
                location=location,
                parameters=parameters,
                return_type=return_type
            )
        )


@dataclass(kw_only=True)
class CFnType(SylvaType):

    @staticmethod
    def build_type(
        location: Location,
        mod: TypeModifier = TypeModifier.NoMod,
        parameters: list[SylvaField] = field(default_factory=list),
        return_type: Optional[SylvaType] = None,
    ) -> MonoCFnType:
        return MonoCFnType(
            location=location, parameters=parameters, return_type=return_type
        )


@dataclass(kw_only=True)
class FnValue(SylvaValue):
    type: MonoFnType


@dataclass(kw_only=True)
class CFnValue(SylvaValue):
    type: MonoCFnType


@dataclass(kw_only=True)
class RuneType(SylvaType):

    @cached_property
    def mname(self):
        return '4rune'


@dataclass(kw_only=True)
class RuneValue(SylvaType):
    type: RuneType
    value: str

    def __post_init__(self):
        if len(self.value) > 1:
            raise errors.InvalidRuneValue('Runes must have len <= 1')


@dataclass(kw_only=True)
class NumericType(SylvaType):
    pass


@dataclass(kw_only=True)
class SizedNumericType(NumericType):
    bits: int


@dataclass(kw_only=True)
class ComplexType(SizedNumericType):

    @cached_property
    def mname(self) -> str:
        return utils.len_prefix(f'c{self.bits}')


@dataclass(kw_only=True)
class ComplexValue(SylvaValue):
    type: ComplexType


@dataclass(kw_only=True)
class FloatType(SizedNumericType):

    @cached_property
    def mname(self) -> str:
        return utils.len_prefix(f'f{self.bits}')


@dataclass(kw_only=True)
class FloatValue(SylvaValue):
    type: FloatType


@dataclass(kw_only=True)
class IntType(SizedNumericType):
    signed: bool

    @cached_property
    def mname(self) -> str:
        return utils.len_prefix(f'{"i" if self.signed else "u"}{self.bits}')


@dataclass(kw_only=True)
class IntValue(SylvaValue):
    type: IntType


@dataclass(kw_only=True)
class MonoRangeType(SylvaType):
    min: Union[IntValue, FloatValue, ComplexValue]
    max: Union[IntValue, FloatValue, ComplexValue]

    def __post_init__(self):
        if self.min.type != self.max.type:
            raise errors.MismatchedRangeTypes(
                self.location, self.min.type, self.max.type
            )
        self.type = min.type

    @cached_property
    def mname(self):
        return self.type.mname


@dataclass(kw_only=True)
class RangeType(SylvaType):

    @staticmethod
    def build_type(
        location: Location,
        min: Union[IntValue, FloatValue, ComplexValue],
        max: Union[IntValue, FloatValue, ComplexValue],
        mod: TypeModifier = TypeModifier.NoMod,
    ) -> MonoRangeType:
        return MonoRangeType(location=location, min=min, max=max)


@dataclass(kw_only=True)
class RangeValue(SylvaValue):
    type: MonoRangeType
    value: Union[complex, float, int]

    def __post_init__(self):
        if self.value < self.type.min or self.value > self.type.max:
            raise errors.InvalidRangeValue(
                self.location, self.value, self.type.min, self.type.max
            )


@dataclass(kw_only=True)
class MonoArrayType(SylvaType):
    element_type: SylvaType
    element_count: int

    def __post_init__(self):
        if self.element_count <= 0:
            raise errors.EmptyArray(self.location)

    @cached_property
    def mname(self):
        return ''.join([
            '1a',
            self.element_type.mname,
            utils.len_prefix(str(self.element_count))
        ])


@dataclass(kw_only=True)
class MonoCArrayType(MonoArrayType):

    @cached_property
    def mname(self):
        return ''.join([
            '2ca',
            self.element_type.mname,
            utils.len_prefix(str(self.element_count))
        ])


@dataclass(kw_only=True)
class MonoStrType(MonoArrayType):
    element_type: SylvaType = field(init=False, default=None)

    def __post_init__(self):
        self.element_type = U8

    @cached_property
    def mname(self):
        return utils.mangle(['3str', self.element_count])


@dataclass(kw_only=True)
class ParamArrayType(SylvaType):
    element_type: SylvaType

    def get_monomorphization(
        self, location: Location, element_count: int
    ) -> MonoArrayType:
        return MonoArrayType(
            location=location,
            element_type=self.element_type,
            element_count=element_count
        )


@dataclass(kw_only=True)
class ParamCArrayType(ParamArrayType):

    @property
    def is_var(self):
        return True

    def get_monomorphization(
        self, location: Location, element_count: int
    ) -> MonoCArrayType:
        return MonoCArrayType(
            location=location,
            element_type=self.element_type,
            element_count=element_count
        )


@dataclass(kw_only=True)
class ParamStrType(ParamArrayType):
    element_type: SylvaType = field(init=False, default=None)

    def __post_init__(self):
        self.element_type = U8

    @property
    def is_var(self):
        return True

    def get_monomorphization(
        self, location: Location, element_count: int
    ) -> MonoStrType:
        return MonoStrType(location=location, element_count=element_count)


@dataclass(kw_only=True)
class ArrayType(SylvaType):

    @staticmethod
    def build_type(
        location: Location,
        element_type: SylvaType,
        element_count: Optional[int] = None,
        mod: TypeModifier = TypeModifier.NoMod,
    ) -> Union[MonoArrayType, ParamArrayType]:
        return (
            MonoArrayType(
                location=location,
                element_type=element_type,
                element_count=element_count
            ) if element_count is not None else
            ParamArrayType(location=location, element_type=element_type)
        )


@dataclass(kw_only=True)
class CArrayType(ArrayType):

    @staticmethod
    def build_type(
        location: Location,
        element_type: SylvaType,
        element_count: Optional[int] = None,
        mod: TypeModifier = TypeModifier.NoMod,
    ) -> Union[MonoCArrayType, ParamCArrayType]:
        return (
            MonoCArrayType(
                location=location,
                element_type=element_type,
                element_count=element_count
            ) if element_count is not None else
            ParamCArrayType(location=location, element_type=element_type)
        )


@dataclass(kw_only=True)
class ArrayValue(SylvaValue):
    type: MonoArrayType
    value: list


@dataclass(kw_only=True)
class CArrayValue(SylvaValue):
    type: MonoCArrayType
    value: list


@dataclass(kw_only=True)
class MonoCBitFieldType(SylvaType):
    bits: int
    signed: bool
    field_size: int

    @cached_property
    def mname(self):
        return utils.mangle(['cbf', self.bits, self.signed, self.field_size])


@dataclass(kw_only=True)
class CBitFieldType(SylvaType):

    @staticmethod
    def build_type(
        location: Location,
        bits: int,
        signed: bool,
        field_size: int,
        mod: TypeModifier = TypeModifier.NoMod,
    ) -> MonoCBitFieldType:
        return MonoCBitFieldType(
            location=location, bits=bits, signed=signed, field_size=field_size
        )


@dataclass(kw_only=True)
class CBitFieldValue(SylvaValue):
    type: CBitFieldType
    value: int

    def __post_init__(self):
        if utils.bits_required_for_int(self.value) > self.type.field_size:
            raise errors.InvalidBitFieldValue(self.value)


@dataclass(kw_only=True)
class StrType(ArrayType):

    @staticmethod
    def build_type(
        location: Location,
        mod: TypeModifier = TypeModifier.NoMod,
        element_count: Optional[int] = None
    ) -> Union[MonoStrType, ParamStrType]:
        return (
            MonoStrType(location=location, element_count=element_count)
            if element_count is not None else ParamStrType(location=location)
        )


@dataclass(kw_only=True)
class StrValue(SylvaValue):
    type: MonoStrType
    value: str


@dataclass(kw_only=True)
class MonoDynarrayType(SylvaType):
    element_type: SylvaType

    # [NOTE] This isn't a struct with pre-defined fields because Sylva (mostly)
    #        can't represent raw pointers.

    @cached_property
    def mname(self):
        return ''.join(['2da', self.element_type.mname])


@dataclass(kw_only=True)
class ParamDynarrayType(SylvaType):

    @property
    def is_var(self):
        return True

    def get_monomorphization(
        self, location: Location, element_type: SylvaType
    ) -> MonoDynarrayType:
        return MonoDynarrayType(location=location, element_type=element_type)


@dataclass(kw_only=True)
class DynarrayType(SylvaType):

    @staticmethod
    def build_type(
        location: Location,
        mod: TypeModifier = TypeModifier.NoMod,
        element_type: Optional[SylvaType] = None,
    ) -> Union[MonoDynarrayType, ParamDynarrayType]:
        return ( # yapf: ignore
            MonoDynarrayType(location=location, element_type=element_type)
            if element_type is not None
            else ParamDynarrayType(location=location)
        )


@dataclass(kw_only=True)
class DynarrayValue(SylvaValue):
    type: MonoDynarrayType
    value: list


@dataclass(kw_only=True)
class StringType(MonoDynarrayType):
    element_type: SylvaType = field(init=False, default=None)

    def __post_init__(self):
        self.element_type = U8

    @cached_property
    def mname(self):
        return '6string'


@dataclass(kw_only=True)
class StringValue(SylvaValue):
    type: StringType
    value: str


@dataclass(kw_only=True)
class MonoStructType(SylvaType):
    fields: list[SylvaField] = field(default_factory=list)

    @cached_property
    def mname(self):
        return ''.join('6struct', ''.join(f.type.mname for f in self.fields))


@dataclass(kw_only=True)
class ParamStructType(SylvaType):
    fields: list[SylvaField] = field(default_factory=list)

    @property
    def is_var(self):
        return True

    @cached_property
    def var_fields(self):
        return list(
            itertools.chain(
                *([[f for f in self.fields if f.is_var]] + [
                    f.var_fields
                    for f in self.fields
                    if hasattr(f, 'var_fields')
                ])
            )
        )

    def get_monomorphization(
        self, location: Location, fields: list[SylvaField]
    ) -> MonoStructType:
        # Check that all param fields are specified
        if len(fields) != len(self.var_fields):
            raise errors.MismatchedTypeParams(location, self.var_fields)

        ifields = iter(fields)

        # [FIXME] Normally we have access to the type when building fields,
        #         meaning that building self-referential fields is easy. But
        #         here we've wrapped that all up in this method, so it's
        #         currently not possible to create a struct monomorphization
        #         with a self-referential field. I think the fix here is
        #         something like a `SelfReferentialField`, probably.

        return MonoStructType(
            location=location,
            fields=[f if not f.is_var else next(ifields) for f in self.fields]
        )


@dataclass(kw_only=True)
class StructType(SylvaType):

    @staticmethod
    def build_type(
        location: Location,
        fields: list[SylvaField],
        mod: TypeModifier = TypeModifier.NoMod,
    ) -> Union[MonoStructType, ParamStructType]:
        return (
            ParamStructType(location=location, fields=fields) if any(
                f.is_var for f in fields
            ) else MonoStructType(location=location, fields=fields)
        )


@dataclass(kw_only=True)
class StructValue(SylvaValue):
    type: MonoStructType
    value: dict


@dataclass(kw_only=True)
class MonoVariantType(MonoStructType):

    @cached_property
    def mname(self):
        return ''.join('7variant', ''.join(f.type.mname for f in self.fields))

    # def set_fields(self, fields):
    #     dupes = utils.get_dupes(f.name for f in fields)
    #     if dupes:
    #         raise errors.DuplicateFields(self, dupes)

    #     llvm_fields = []
    #     largest_field = None

    #     seen = set()
    #     self.type_parameters = []

    #     for f in fields:
    #         llvm_fields.append(f.type.llvm_type)

    #         self._type_parameters.extend([
    #             tp for tp in f.type_parameters
    #             if tp.name not in seen and not seen.add(tp.name)
    #         ])

    #         if largest_field is None:
    #             largest_field = f
    #             continue

    #         if f.type.get_size() > largest_field.type.get_size():
    #             largest_field = f

    #     if self.name:
    #         self.llvm_type.set_body(
    #             largest_field.type.llvm_type,
    #             ir.IntType(utils.round_up_to_power_of_two(len(fields)))
    #         )
    #     else:
    #         self.llvm_type = ir.LiteralStructType([
    #             largest_field.type.llvm_type,
    #             ir.IntType(utils.round_up_to_power_of_two(len(fields)))
    #         ])

    #     self.fields = fields


@dataclass(kw_only=True)
class ParamVariantType(ParamStructType):

    @property
    def is_var(self):
        return True

    def get_monomorphization(
        self, location: Location, fields: list[SylvaField]
    ) -> MonoVariantType:
        if len(fields) != len(self.var_fields):
            raise errors.MismatchedTypeParams(location, self.var_fields)

        ifields = iter(fields)

        # [FIXME] Normally we have access to the type when building fields,
        #         meaning that building self-referential fields is easy. But
        #         here we've wrapped that all up in this method, so it's
        #         currently not possible to create a struct monomorphization
        #         with a self-referential field. I think the fix here is
        #         something like a `SelfReferentialField`, probably.

        return MonoVariantType(
            location=location,
            fields=[f if not f.is_var else next(ifields) for f in self.fields]
        )


@dataclass(kw_only=True)
class VariantType(StructType):

    @staticmethod
    def build_type(
        location: Location,
        fields: list[SylvaField],
        mod: TypeModifier = TypeModifier.NoMod,
    ) -> Union[MonoVariantType, ParamVariantType]:
        return (
            ParamVariantType(location=location, fields=fields) if any(
                f.is_var for f in fields
            ) else MonoVariantType(location=location, fields=fields)
        )


@dataclass(kw_only=True)
class VariantValue(SylvaValue):
    type: MonoVariantType
    value: dict


@dataclass(kw_only=True)
class CStructType(MonoStructType):

    @cached_property
    def mname(self):
        return 'cstruct'


@dataclass(kw_only=True)
class CStructValue(SylvaValue):
    type: CStructType
    value: dict


@dataclass(kw_only=True)
class CUnionType(MonoStructType):

    @cached_property
    def mname(self):
        return ''.join(['6cunion', ''.join(f.type.mname for f in self.fields)])


@dataclass(kw_only=True)
class CUnionValue(SylvaValue):
    type: CUnionType
    value: dict


C16 = ComplexType(bits=16)
C32 = ComplexType(bits=32)
C64 = ComplexType(bits=64)
C128 = ComplexType(bits=128)
F16 = FloatType(bits=16)
F32 = FloatType(bits=32)
F64 = FloatType(bits=64)
F128 = FloatType(bits=128)
I8 = IntType(bits=8, signed=True)
I16 = IntType(bits=16, signed=True)
I32 = IntType(bits=32, signed=True)
I64 = IntType(bits=64, signed=True)
I128 = IntType(bits=128, signed=True)
U8 = IntType(bits=8, signed=False)
U16 = IntType(bits=16, signed=False)
U32 = IntType(bits=32, signed=False)
U64 = IntType(bits=64, signed=False)
U128 = IntType(bits=128, signed=False)
BOOL = BoolType()
RUNE = RuneType()
ARRAY = ArrayType()
CARRAY = CArrayType()
STR = StrType()
DYNARRAY = DynarrayType()
STRUCT = StructType()
CBITFIELD = CBitFieldType()
CFN = CFnType()
CPTR = CPtrType()
CSTR = CStrType()  # [NOTE] Should this also inherit from CARRAY or w/e?
CSTRUCT = CStructType()
CUNION = CUnionType()
CVOID = CVoidType()
CVOIDEX = CVoidType(is_exclusive=True)
ENUM = EnumType()
FN = FnType()
RANGE = RangeType()
RUNE = RuneType()
STRING = StringType()
STRUCT = StructType()
VARIANT = VariantType()


def lookup(name):
    return {
        # 'String',
        'bool': BOOL,
        'c128': C128,
        'c16': C16,
        'c32': C32,
        'c64': C64,
        'f128': F128,
        'f16': F16,
        'f32': F32,
        'f64': F64,
        'i128': I128,
        'i16': I16,
        'i32': I32,
        'i64': I64,
        'i8': I8,
        'int': ( # yapf: ignore
            I8 if _SIZE_SIZE == 8 else
            I16 if _SIZE_SIZE == 16 else
            I32 if _SIZE_SIZE == 32 else
            I64 if _SIZE_SIZE == 64 else
            I128 if _SIZE_SIZE == 128 else
            None
        ),
        'rune': RUNE,
        'str': STR,  # 'string': STRING,
        'u128': U128,
        'u16': U16,
        'u32': U32,
        'u64': U64,
        'u8': U8,
        'uint': ( # yapf: ignore
            U8 if _SIZE_SIZE == 8 else
            U16 if _SIZE_SIZE == 16 else
            U32 if _SIZE_SIZE == 32 else
            U64 if _SIZE_SIZE == 64 else
            U128 if _SIZE_SIZE == 128 else
            None
        ),
    }.get(name)


@dataclass(kw_only=True, slots=True)
class TypeDef(SylvaObject):
    name: str
    type: SylvaType


# @dataclass(kw_only=True)
# class ArrayTypeLiteralExpr(SylvaObject):
#     mod: TypeModifier
#     element_type_expr: Union[  # yapf: ignore
#         CArrayTypeLiteralExpr,  # yapf: ignore
#         CBitFieldTypeLiteralExpr,
#         CBlockFnLiteralExpr,
#         CFnLiteralExpr,
#         CPtrLiteralExpr,
#         CStructLiteralExpr,
#         CUnionLiteralExpr,
#         CVoidLiteralExpr,
#         FnTypeLiteralExpr,
#         RangeTypeLiteralExpr,
#         Self,
#         StructTypeLiteralExpr,
#         TypePlaceholder,
#         VarTypeExpr]
#     element_count_expr: Optional[Union[ConstLookupExpr, IntLiteralExpr]]
#
#     @property
#     def is_parameterizable(self):
#         return isinstance(self.type_expr, TypePlaceholder)

# @dataclass(kw_only=True)
# class CArrayTypeLiteralExpr(SylvaObject):
#     mod: TypeModifier
#     element_type_expr: Union[  # yapf: ignore
#         ArrayTypeLiteralExpr,  # yapf: ignore
#         CBitFieldTypeLiteralExpr,
#         CBlockFnLiteralExpr,
#         CFnLiteralExpr,
#         CPtrLiteralExpr,
#         CStructLiteralExpr,
#         CUnionLiteralExpr,
#         CVoidLiteralExpr,
#         FnTypeLiteralExpr,
#         RangeTypeLiteralExpr,
#         Self,
#         StructTypeLiteralExpr,
#         TypePlaceholder,
#         VarTypeExpr]
#     element_count_expr: Union[ConstLookupExpr, IntLiteralExpr]

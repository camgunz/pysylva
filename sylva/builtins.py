import enum
import itertools

from dataclasses import dataclass, field
from functools import cached_property
from typing import Any, Literal, Optional, Tuple, Union

import lark

from sylva import _SIZE_SIZE, debug, errors, utils
from sylva.location import Location


class TypeModifier(enum.Enum):
    NoMod = enum.auto()
    Ptr = enum.auto()
    Ref = enum.auto()
    ExRef = enum.auto()
    CMut = enum.auto()

    @classmethod
    def separate_type_mod(cls, parts: list):
        if not isinstance(parts[0], lark.Token):
            if isinstance(parts[-1], lark.Token) and parts[-1].value == '!':
                return (cls.CMut, parts[1:-1])

            return (cls.NoMod, parts)

        first_child = parts[0].value

        if first_child == '*':
            return (cls.Ptr, parts[1:])

        if not first_child == '&':
            return (cls.NoMod, parts)

        if isinstance(parts[-1], lark.Token) and parts[-1].value == '!':
            return (cls.ExRef, parts[1:-1])

        return (cls.Ref, parts[1:])


@dataclass(kw_only=True)
class SylvaObject:
    location: Optional[Location] = None

    def __post_init__(self):
        self.location = self.location or Location.Generate()


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

    def __post_init__(self):
        if self.type is None:
            debug(
                'nonetype',
                f'{self.name} (self.location.shorthand): type is None'
            )

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


@dataclass(kw_only=True)
class Type(SylvaType):

    @cached_property
    def mname(self):
        return '4type'


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
            TypeModifier.CMut, TypeModifier.ExRef, TypeModifier.Ptr
        )


@dataclass(kw_only=True)
class ParamCPtrType(SylvaType):

    @property
    def is_var(self):
        return True

    def get_monomorphization(
        self,
        referenced_type: SylvaType,
        location: Optional[Location] = None,
    ) -> MonoCPtrType:
        location = location if location else Location.Generate()
        return MonoCPtrType(location=location, referenced_type=referenced_type)


@dataclass(kw_only=True)
class CPtrType(SylvaType):

    @staticmethod
    def build_type(
        referenced_type: Optional[SylvaType] = None,
        location: Optional[Location] = None,
        mod: TypeModifier = TypeModifier.NoMod,
    ) -> Union[MonoCPtrType, ParamCPtrType]:
        location = location if location else Location.Generate()
        return ( # yapf: ignore
            MonoCPtrType(
                location=location,
                mod=mod,
                referenced_type=referenced_type,
            )
            if referenced_type is not None
            else ParamCPtrType(location=location)
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
    def first_value(self):
        return next(iter(self.values.values()))

    @cached_property
    def mname(self):
        return ''.join(['1e', self.first_value.type.mname])

    @cached_property
    def type(self):
        return self.first_value.type


@dataclass(kw_only=True)
class EnumType(SylvaType):

    @staticmethod
    def build_type(
        values: dict[str, SylvaValue],
        location: Optional[Location] = None,
        mod: TypeModifier = TypeModifier.NoMod,
    ) -> MonoEnumType:
        location = location if location else Location.Generate()
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
class MonoCBlockFnType(SylvaType):
    parameters: list[SylvaField] = field(default_factory=list)
    return_type: Optional[SylvaType]

    def __post_init__(self):
        if dupes := utils.get_dupes(p.name for p in self.parameters):
            raise errors.DuplicateParameters(self, dupes)

    @cached_property
    def mname(self):
        return ''.join([
            '4bcfn',
            ''.join(p.type.mname for p in self.parameters),
            self.return_type.mname if self.return_type else '1v'
        ])


@dataclass(kw_only=True)
class ParamFnType(SylvaType):
    parameters: list[SylvaField] = field(default_factory=list)
    return_type: Optional[SylvaType] = None
    return_type_param: Optional[SylvaField] = None

    def __post_init__(self):
        if self.return_type and self.return_type_param:
            raise ValueError(
                'Cannot specify both return_type and return_type_param'
            )

    @property
    def return_type_param_name(self):
        return (
            None if not self.return_type_param else self.return_type_param.name
        )

    @property
    def type_parameters(self):
        return ([p.name for p in self.parameters if p.is_var] +
                ([self.return_type_param] if self.return_type_param else []))

    @property
    def return_type_must_be_inferred(self):
        return bool(self.return_type_param)

    def get_monomorphization(
        self,
        parameters: list[SylvaField],
        return_type: Optional[SylvaType],
        location: Optional[Location] = None,
    ) -> MonoFnType:
        location = location if location else Location.Generate()
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
        parameters: list[SylvaField] = field(default_factory=list),
        return_type: Optional[SylvaType] = None,
        location: Optional[Location] = None,
        mod: TypeModifier = TypeModifier.NoMod,
    ) -> Union[MonoFnType, ParamFnType]:
        location = location if location else Location.Generate()
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
        parameters: list[SylvaField] = field(default_factory=list),
        return_type: Optional[SylvaType] = None,
        location: Optional[Location] = None,
        mod: TypeModifier = TypeModifier.NoMod,
    ) -> MonoCFnType:
        location = location if location else Location.Generate()
        return MonoCFnType(
            location=location, parameters=parameters, return_type=return_type
        )


@dataclass(kw_only=True)
class CBlockFnType(SylvaType):

    @staticmethod
    def build_type(
        parameters: list[SylvaField] = field(default_factory=list),
        return_type: Optional[SylvaType] = None,
        location: Optional[Location] = None,
        mod: TypeModifier = TypeModifier.NoMod,
    ) -> MonoCBlockFnType:
        location = location if location else Location.Generate()
        return MonoCBlockFnType(
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

    @classmethod
    def FromString(
        cls,
        strval: str,
        location: Optional[Location] = None,
    ):
        if strval.endswith('f16'):
            return cls(location=location, type=C16, value=complex(strval[:-3]))
        if strval.endswith('f32'):
            return cls(location=location, type=C32, value=complex(strval[:-3]))
        if strval.endswith('f64'):
            return cls(location=location, type=C64, value=complex(strval[:-3]))
        if strval.endswith('f128'):
            return cls(
                location=location, type=C128, value=complex(strval[:-4])
            )

        raise ValueError(f'Malformed complex value {strval}')


@dataclass(kw_only=True)
class FloatType(SizedNumericType):

    @cached_property
    def mname(self) -> str:
        return utils.len_prefix(f'f{self.bits}')


@dataclass(kw_only=True)
class FloatValue(SylvaValue):
    type: FloatType

    @classmethod
    def FromString(
        cls,
        strval: str,
        location: Optional[Location] = None,
    ):
        if strval.endswith('f16'):
            return cls(location=location, type=F16, value=float(strval[:-3]))
        if strval.endswith('f32'):
            return cls(location=location, type=F32, value=float(strval[:-3]))
        if strval.endswith('f64'):
            return cls(location=location, type=F64, value=float(strval[:-3]))
        if strval.endswith('f128'):
            return cls(location=location, type=F128, value=float(strval[:-4]))

        raise ValueError(f'Malformed float value {strval}')


@dataclass(kw_only=True)
class IntType(SizedNumericType):
    signed: bool

    @cached_property
    def mname(self) -> str:
        return utils.len_prefix(f'{"i" if self.signed else "u"}{self.bits}')


@dataclass(kw_only=True)
class IntValue(SylvaValue):
    type: IntType

    @classmethod
    def FromString(cls, location: Location, strval: str):
        int_type, value = parse_int_value(location=location, strval=strval)
        return IntValue(location=location, type=int_type, value=value)


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
        min: Union[IntValue, FloatValue, ComplexValue],
        max: Union[IntValue, FloatValue, ComplexValue],
        location: Optional[Location] = None,
        mod: TypeModifier = TypeModifier.NoMod,
    ) -> MonoRangeType:
        location = location if location else Location.Generate()
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
    element_count: IntValue

    def __post_init__(self):

        if self.element_count.value <= 0:
            raise errors.InvalidArraySize(self.location)

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
class ParamArrayType(SylvaType):
    element_type: SylvaType

    def get_monomorphization(
        self,
        element_count: IntValue,
        location: Optional[Location] = None,
    ) -> MonoArrayType:
        location = location if location else Location.Generate()
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
        self,
        element_count: IntValue,
        location: Optional[Location] = None,
    ) -> MonoCArrayType:
        location = location if location else Location.Generate()
        return MonoCArrayType(
            location=location,
            element_type=self.element_type,
            element_count=element_count
        )


@dataclass(kw_only=True)
class ArrayType(SylvaType):

    @staticmethod
    def build_type(
        element_type: SylvaType,
        element_count: Optional[IntValue] = None,
        location: Optional[Location] = None,
        mod: TypeModifier = TypeModifier.NoMod,
    ) -> Union[MonoArrayType, ParamArrayType]:
        location = location if location else Location.Generate()
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
        element_type: SylvaType,
        element_count: Optional[IntValue] = None,
        location: Optional[Location] = None,
        mod: TypeModifier = TypeModifier.NoMod,
    ) -> Union[MonoCArrayType, ParamCArrayType]:
        location = location if location else Location.Generate()
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
        bits: int,
        signed: bool,
        field_size: int,
        location: Optional[Location] = None,
        mod: TypeModifier = TypeModifier.NoMod,
    ) -> MonoCBitFieldType:
        location = location if location else Location.Generate()
        return MonoCBitFieldType(
            location=location, bits=bits, signed=signed, field_size=field_size
        )


@dataclass(kw_only=True)
class CBitFieldValue(SylvaValue):
    type: CBitFieldType
    value: int

    def __post_init__(self):
        if utils.bits_required_for_int(self.value) > self.type.field_size:
            raise errors.CBitFieldSizeExceeded(
                self.value, self.type.field_size
            )


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
        self,
        element_type: SylvaType,
        location: Optional[Location] = None
    ) -> MonoDynarrayType:
        location = location if location else Location.Generate()
        return MonoDynarrayType(location=location, element_type=element_type)


@dataclass(kw_only=True)
class DynarrayType(SylvaType):

    @staticmethod
    def build_type(
        element_type: Optional[SylvaType] = None,
        location: Optional[Location] = None,
        mod: TypeModifier = TypeModifier.NoMod,
    ) -> Union[MonoDynarrayType, ParamDynarrayType]:
        location = location if location else Location.Generate()
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
class MonoStructType(SylvaType):
    fields: list[SylvaField] = field(default_factory=list)

    @property
    def mname(self):
        return ''.join('6struct', ''.join(f.type.mname for f in self.fields))


@dataclass(kw_only=True)
class ParamStructType(SylvaType):
    fields: list[SylvaField] = field(default_factory=list)

    @property
    def is_var(self):
        return True

    @property
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
        self,
        fields: Optional[list[SylvaField]],
        location: Optional[Location] = None,
    ) -> MonoStructType:
        location = location if location else Location.Generate()
        fields = fields if fields else []
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
        fields: Optional[list[SylvaField]] = None,
        location: Optional[Location] = None,
        mod: TypeModifier = TypeModifier.NoMod,
    ) -> Union[MonoStructType, ParamStructType]:
        location = location if location else Location.Generate()
        fields = fields if fields else []
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
        self,
        fields: Optional[list[SylvaField]] = None,
        location: Optional[Location] = None,
    ) -> MonoVariantType:
        location = location if location else Location.Generate()
        fields = fields if fields else []
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
        fields: Optional[list[SylvaField]] = None,
        location: Optional[Location] = None,
        mod: TypeModifier = TypeModifier.NoMod,
    ) -> Union[MonoVariantType, ParamVariantType]:
        location = location if location else Location.Generate()
        fields = fields if fields else []
        return (
            ParamVariantType(location=location, mod=mod, fields=fields) if any(
                f.is_var for f in fields
            ) else MonoVariantType(location=location, mod=mod, fields=fields)
        )


@dataclass(kw_only=True)
class VariantValue(SylvaValue):
    type: MonoVariantType
    value: dict


@dataclass(kw_only=True)
class MonoCStructType(MonoStructType):

    @cached_property
    def mname(self):
        return 'cstruct'


@dataclass(kw_only=True)
class CStructType(StructType):

    @staticmethod
    def build_type(
        fields: Optional[list[SylvaField]] = None,
        location: Optional[Location] = None,
        mod: TypeModifier = TypeModifier.NoMod,
    ) -> MonoCStructType:
        location = location if location else Location.Generate()
        return MonoCStructType(
            location=location, mod=mod, fields=fields if fields else []
        )


@dataclass(kw_only=True)
class CStructValue(SylvaValue):
    type: CStructType
    value: dict


@dataclass(kw_only=True)
class MonoCUnionType(MonoStructType):

    @cached_property
    def mname(self):
        return ''.join(['6cunion', ''.join(f.type.mname for f in self.fields)])


@dataclass(kw_only=True)
class CUnionType(SylvaType):

    @staticmethod
    def build_type(
        fields: Optional[list[SylvaField]] = None,
        location: Optional[Location] = None,
        mod: TypeModifier = TypeModifier.NoMod,
    ) -> MonoCUnionType:
        location = location if location else Location.Generate()
        return MonoCUnionType(
            location=location, mod=mod, fields=fields if fields else []
        )


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
DYNARRAY = DynarrayType()
STRUCT = StructType()
CBITFIELD = CBitFieldType()
CBLOCKFN = CBlockFnType()
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
STRUCT = StructType()
TYPE = Type()
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


@dataclass(kw_only=True)
class MonoStrType(MonoArrayType):
    element_type: SylvaType = field(init=False, default_factory=lambda: U8)

    def __post_init__(self):
        self.element_type = U8

    @cached_property
    def mname(self):
        return utils.mangle(['3str', self.element_count])


@dataclass(kw_only=True)
class ParamStrType(ParamArrayType):
    element_type: SylvaType = field(init=False, default_factory=lambda: U8)

    def __post_init__(self):
        self.element_type = U8

    @property
    def is_var(self):
        return True

    def get_monomorphization(
        self,
        element_count: IntValue,
        location: Optional[Location] = None,
    ) -> MonoStrType:
        location = location if location else Location.Generate()
        return MonoStrType(location=location, element_count=element_count)


@dataclass(kw_only=True)
class StrType(ArrayType):

    @staticmethod
    def build_type( # type: ignore
        element_count: Optional[IntValue] = None,
        location: Optional[Location] = None,
        mod: TypeModifier = TypeModifier.NoMod,
    ) -> Union[MonoStrType, ParamStrType]:
        location = location if location else Location.Generate()
        return (
            MonoStrType(location=location, element_count=element_count)
            if element_count is not None else ParamStrType(location=location)
        )


@dataclass(kw_only=True)
class StrValue(SylvaValue):
    type: MonoStrType
    value: str


@dataclass(kw_only=True)
class StringType(MonoDynarrayType):
    element_type: SylvaType = field(init=False, default_factory=lambda: U8)

    def __post_init__(self):
        self.element_type = U8

    @cached_property
    def mname(self):
        return '6string'


@dataclass(kw_only=True)
class StringValue(SylvaValue):
    type: StringType
    value: str


@dataclass(kw_only=True, slots=True)
class TypeDef(SylvaObject):
    name: str
    type: SylvaType


@dataclass(kw_only=True)
class TypePlaceholder(SylvaType):
    name: str

    @property
    def is_var(self):
        return True


@dataclass(kw_only=True)
class SelfReferentialField(SylvaObject):
    name: str


STR = StrType()
STRING = StringType()


def get_int_base(int_value: str) -> Literal[2, 8, 10, 16]:
    if int_value.startswith('0b') or int_value.startswith('0B'):
        return 2
    if int_value.startswith('0o') or int_value.startswith('0O'):
        return 8
    if int_value.startswith('0x') or int_value.startswith('0X'):
        return 16
    return 10


def get_int_type(bits: Optional[int], signed: bool) -> IntType:
    bits = bits if bits else _SIZE_SIZE
    if signed and bits == 8:
        return I8
    if signed and bits == 16:
        return I16
    if signed and bits == 32:
        return I32
    if signed and bits == 64:
        return I64
    if signed and bits == 128:
        return I128
    if bits == 8:
        return U8
    if bits == 16:
        return U16
    if bits == 32:
        return U32
    if bits == 64:
        return U64
    if bits == 128:
        return U128

    raise ValueError(
        f'Unable to determine int type for bits={bits}, signed={signed}'
    )


def parse_int_value( # yapf: ignore
    strval: str,
    location: Optional[Location] = None,
) -> Tuple[IntType, int]:
    base = get_int_base(strval)
    signed = (
        strval.endswith('i') or strval.endswith('i8') or
        strval.endswith('i16') or strval.endswith('i32') or
        strval.endswith('i64') or strval.endswith('i128')
    )
    try:
        int_type = get_int_type(
            bits=( # yapf: ignore
                8 if strval.endswith('8') else
                16 if strval.endswith('16') else
                32 if strval.endswith('32') else
                64 if strval.endswith('64') else
                128 if strval.endswith('128') else
                None
            ),
            signed=signed
        )
    except ValueError as e:
        raise errors.LiteralParseFailure(location, 'int', str(e)) from None

    value = ( # yapf: ignore
        int(strval[:-1], base=base) if strval.endswith('i') else
        int(strval[:-1], base=base) if strval.endswith('u') else
        int(strval[:-2], base=base) if strval.endswith('i8') else
        int(strval[:-3], base=base) if strval.endswith('i16') else
        int(strval[:-3], base=base) if strval.endswith('i32') else
        int(strval[:-3], base=base) if strval.endswith('i64') else
        int(strval[:-4], base=base) if strval.endswith('i128') else
        int(strval[:-2], base=base) if strval.endswith('u8') else
        int(strval[:-3], base=base) if strval.endswith('u16') else
        int(strval[:-3], base=base) if strval.endswith('u32') else
        int(strval[:-3], base=base) if strval.endswith('u64') else
        int(strval[:-4], base=base) if strval.endswith('u128') else
        int(strval, base=base)
    )

    return (int_type, value)


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

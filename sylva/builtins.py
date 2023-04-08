import enum
import itertools

from collections import defaultdict
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any, Self, TYPE_CHECKING, Union

import lark

from sylva import _SIZE_SIZE, errors, utils
from sylva.location import Location

if TYPE_CHECKING:
    from sylva.expr import Expr
    from sylva.mod import Mod
    from sylva.stmt import Stmt


_TYPE_NAME_COUNTS: defaultdict = defaultdict(lambda: 1)


def gen_name(namespace: str, force_number: bool = False) -> str:
    count = _TYPE_NAME_COUNTS[namespace]
    type_name = (  # yapf: ignore
        f'{namespace}{count}'
        if count > 1 or force_number
        else namespace
    )
    _TYPE_NAME_COUNTS[namespace] += 1
    return type_name


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
    location: Location = field(default_factory=Location.Generate)
    module: 'Mod'


@dataclass(kw_only=True)
class NamedSylvaObject(SylvaObject):
    name: str


@dataclass(kw_only=True)
class SylvaType(NamedSylvaObject):
    mod: TypeModifier = TypeModifier.NoMod

    @property
    def is_var(self):
        return False

    def matches(self, other: Self) -> bool:
        return self is other


@dataclass(kw_only=True)
class ParamSylvaType(SylvaType):

    @property
    def is_var(self):
        return True


@dataclass(kw_only=True)
class TypePlaceholder(ParamSylvaType):

    def matches(self, other: SylvaType) -> bool:
        return isinstance(other, TypePlaceholder) and other.name == self.name


@dataclass(kw_only=True)
class SylvaValue(NamedSylvaObject):
    name: str = ''
    type: SylvaType
    value: Any

    def __eq__(self, other):
        return (  # yapf: ignore
            isinstance(other, SylvaValue) and
            self.type.matches(other.type) and
            self.value == other.value
        )


@dataclass(kw_only=True)
class SylvaField(NamedSylvaObject):
    type: SylvaType | None

    @property
    def is_var(self):
        return (
            self.type is None or
            (hasattr(self.type, 'is_var') and self.type.is_var)
        )

    def __eq__(self, other):
        return self.name == other.name and self.type.amtches(other.type)


@dataclass(kw_only=True)
class SylvaDef(NamedSylvaObject):
    value: SylvaValue

    def __post_init__(self):
        if not self.value.name:
            self.value.name = self.name

    @property
    def type(self):
        return self.value.type


@dataclass(kw_only=True)
class Type(SylvaType):
    name: str = field(init=False, default='type')


@dataclass(kw_only=True)
class TypeValue(SylvaValue):
    type: Type
    value: SylvaType


@dataclass(kw_only=True)
class CodeBlock(SylvaObject):
    code: list[Union['Expr', 'Stmt']] = field(default_factory=list)


@dataclass(kw_only=True)
class BoolType(SylvaType):
    name: str = field(init=False, default='bool')


@dataclass(kw_only=True)
class BoolValue(SylvaValue):
    type: BoolType
    value: bool

    @classmethod
    def FromString(
        cls, module: 'Mod', s: str, location: Location | None = None
    ):
        location = location if location else Location.Generate()
        return cls(
            location=location, module=module, type=BOOL, value=s == 'true'
        )


@dataclass(kw_only=True)
class RuneType(SylvaType):
    name: str = field(init=False, default='rune')


@dataclass(kw_only=True)
class RuneValue(SylvaValue):
    type: RuneType
    value: str

    def __post_init__(self):
        if len(self.value) > 1:
            raise errors.invalidRuneValue('Runes must have len <= 1')

    @classmethod
    def FromString(
        cls, module: 'Mod', s: str, location: Location | None = None
    ):
        location = location if location else Location.Generate()
        return cls(location=location, module=module, type=RUNE, value=s)


@dataclass(kw_only=True)
class NumericType(SylvaType):
    pass


@dataclass(kw_only=True)
class SizedNumericType(NumericType):
    bits: int


@dataclass(kw_only=True)
class ComplexType(SizedNumericType):
    name: str = field(init=False, default='')

    def __post_init__(self):
        self.name = f'c{self.bits}'


@dataclass(kw_only=True)
class ComplexValue(SylvaValue):
    type: ComplexType

    @classmethod
    def FromString(
        cls,
        module: 'Mod',
        s: str,
        location: Location | None,
    ):
        location = location if location else Location.Generate()
        if s.endswith('f16'):
            return cls(
                location=location,
                module=module,
                type=C16,
                value=complex(s[:-3])
            )
        if s.endswith('f32'):
            return cls(
                location=location,
                module=module,
                type=C32,
                value=complex(s[:-3])
            )
        if s.endswith('f64'):
            return cls(
                location=location,
                module=module,
                type=C64,
                value=complex(s[:-3])
            )
        if s.endswith('f128'):
            return cls(
                location=location,
                module=module,
                type=C128,
                value=complex(s[:-4])
            )

        raise ValueError(f'Malformed complex value {s}')


@dataclass(kw_only=True)
class FloatType(SizedNumericType):
    name: str = field(init=False, default='')

    def __post_init__(self):
        self.name = f'f{self.bits}'


@dataclass(kw_only=True)
class FloatValue(SylvaValue):
    type: FloatType

    @classmethod
    def FromString(
        cls, module: 'Mod', s: str, location: Location | None = None
    ):
        location = location if location else Location.Generate()
        try:
            type_and_val = ( # yapf: ignore
                (F16,  float(s[:-3])) if s.endswith('16')
                else (F32,  float(s[:-3])) if s.endswith('32')
                else (F64,  float(s[:-3])) if s.endswith('64')
                else (F128, float(s[:-4])) if s.endswith('128')
                else None
            )
        except ValueError as e:
            raise errors.LiteralParseFailure(
                location, 'float', s, str(e)
            ) from None

        if type_and_val is None:
            raise errors.LiteralParseFailure(location, 'float', s)

        type, val = type_and_val

        return cls(location=location, module=module, type=type, value=val)


@dataclass(kw_only=True)
class IntType(SizedNumericType):
    signed: bool
    name: str = field(default='')

    def __post_init__(self):
        if self.name != '':
            raise Exception('Non-blank name given to IntType')

        self.name = (
            f'{"i" if self.signed else "u"}{self.bits if self.bits else ""}'
        )

    # @property
    # def name(self):
    #     return self._name

    # @name.setter
    # def name(self, new_name: str):
    #     breakpoint()
    #     self._name = new_name

    @classmethod
    def Native(cls, location: Location | None = None, signed: bool = True):
        location = location if location else Location.Generate()
        ret = ( # yapf: ignore
            I8 if _SIZE_SIZE == 8 and signed
            else U8 if _SIZE_SIZE == 8 and not signed
            else I16 if _SIZE_SIZE == 16 and signed
            else U16 if _SIZE_SIZE == 16 and not signed
            else I32 if _SIZE_SIZE == 32 and signed
            else U32 if _SIZE_SIZE == 32 and not signed
            else I64 if _SIZE_SIZE == 64 and signed
            else U64 if _SIZE_SIZE == 64 and not signed
            else I128 if _SIZE_SIZE == 128 and signed
            else U128 if _SIZE_SIZE == 128 and not signed
            else None
        )

        if ret is None:
            raise ValueError(f'No native int type for bit width {_SIZE_SIZE}')

        return ret

    @classmethod
    def New(
        cls,
        location: Location | None = None,
        bits: int | None = None,
        signed: bool = True
    ):
        location = location if location else Location.Generate()
        bits = bits if bits else _SIZE_SIZE

        if bits == 8:
            return I8 if signed else U8
        if bits == 16:
            return I16 if signed else U16
        if bits == 32:
            return I32 if signed else U32
        if bits == 64:
            return I64 if signed else U64
        if bits == 128:
            return I128 if signed else U128

        raise ValueError(
            f'Unable to determine int type for bits={bits}, signed={signed}'
        )

    @classmethod
    def FromValue(
        cls,
        value: int,
        signed: bool = True,
        location: Location | None = None,
    ):
        location = location if location else Location.Generate()
        return cls.New(
            location=location, bits=utils.smallest_uint(value), signed=signed
        )


@dataclass(kw_only=True)
class IntValue(SylvaValue):
    type: IntType

    def __post_init__(self):
        if utils.bits_required_for_int(self.value) > self.type.bits:
            raise errors.IntSizeExceeded(self.location, self.value)

    @classmethod
    def FromString(
        cls, module: 'Mod', s: str, location: Location | None = None
    ):
        location = location if location else Location.Generate()
        base = (  # yapf: ignore
            2 if s.lower().startswith('0b')
            else 8 if s.lower().startswith('0o')
            else 16 if s.lower().startswith('0x')
            else 10
        )

        try:
            type_and_val = ( # yapf: ignore
                (I8, int(s[:-2], base)) if s.endswith('i8')
                else (U8, int(s[:-2], base)) if s.endswith('u8')
                else (I16, int(s[:-3], base)) if s.endswith('i16')
                else (U16, int(s[:-3], base)) if s.endswith('u16')
                else (I32, int(s[:-3], base)) if s.endswith('i32')
                else (U32, int(s[:-3], base)) if s.endswith('u32')
                else (I64, int(s[:-3], base)) if s.endswith('i64')
                else (U64, int(s[:-3], base)) if s.endswith('u64')
                else (I128, int(s[:-4], base)) if s.endswith('i128')
                else (U128, int(s[:-4], base)) if s.endswith('u128')
                else (IntType.Native(), int(s[:-1], base)) if s.endswith('i')
                else (IntType.Native(signed=False), int(s[:-1], base))
                    if s.endswith('u')
                else None
            )
        except ValueError as e:
            raise errors.LiteralParseFailure(
                location, 'int', s, str(e)
            ) from None

        if type_and_val is None:
            raise errors.LiteralParseFailure(
                location, 'int', s, 'Invalid suffix'
            )

        type, val = type_and_val

        return cls(location=location, module=module, value=val, type=type)

    @classmethod
    def FromValue(
        cls,
        module: 'Mod',
        n: int,
        signed: bool = True,
        location: Location | None = None
    ):
        location = location if location else Location.Generate()
        return cls(
            location=location,
            module=module,
            type=IntType.FromValue(location=location, value=n),
            value=n
        )

    @classmethod
    def Native(
        cls,
        module: 'Mod',
        n: int,
        signed: bool = True,
        location: Location | None = None
    ):
        location = location if location else Location.Generate()
        return cls(
            location=location,
            module=module,
            type=IntType.Native(location=location, signed=signed),
            value=n
        )


@dataclass(kw_only=True)
class MonoArrayType(SylvaType):
    name: str = field(default_factory=lambda: gen_name('array'))
    element_type: SylvaType
    element_count: IntValue

    def __post_init__(self):
        if self.element_count.value <= 0:
            raise errors.InvalidArraySize(self.location)

    def matches(self, other: SylvaType) -> bool:
        return (
            isinstance(other, MonoArrayType) and
            self.element_type.matches(other.element_type) and
            self.element_count == other.element_count
        )

    def lookup(self, name: str):
        from sylva.expr import IntLiteralExpr
        from sylva.stmt import ReturnStmt

        if name == 'get_length':
            return FnValue(
                module=self.module,
                name='get_length',
                type=MonoFnType(
                    module=self.module,
                    return_type=self.element_count.type,
                ),
                value=CodeBlock(
                    module=self.module,
                    code=[
                        ReturnStmt(
                            module=self.module,
                            expr=IntLiteralExpr(
                                module=self.module,
                                type=self.element_count.type,
                                value=self.element_count
                            )
                        )
                    ]
                )
            )
            pass

    def reflection_lookup(self, name):
        pass


@dataclass(kw_only=True)
class ParamArrayType(ParamSylvaType):
    name: str = field(default_factory=lambda: gen_name('array'))
    element_type: SylvaType

    def get_or_create_monomorphization(
        self,
        module: 'Mod',
        element_count: IntValue,
        location: Location | None = None,
    ) -> MonoArrayType:
        location = location if location else Location.Generate()
        return MonoArrayType(
            location=location,
            module=module,
            element_type=self.element_type,
            element_count=element_count
        )

    def matches(self, other: SylvaType) -> bool:
        return (
            isinstance(other, (MonoArrayType, ParamArrayType)) and
            self.element_type.matches(other.element_type)
        )


@dataclass(kw_only=True)
class ArrayType(SylvaType):
    name: str = field(default_factory=lambda: gen_name('array'))

    @staticmethod
    def build_type(
        module: 'Mod',
        element_type: SylvaType,
        element_count: IntValue | None,
        name: str = '',
        location: Location | None = None,
        mod: TypeModifier = TypeModifier.NoMod,
    ) -> MonoArrayType | ParamArrayType:
        location = location if location else Location.Generate()
        if element_count is not None:
            return MonoArrayType(
                location=location,
                module=module,
                name=name,
                element_type=element_type,
                element_count=element_count
            )

        return ParamArrayType(
            location=location,
            module=module,
            name=name,
            element_type=element_type
        )


@dataclass(kw_only=True)
class ArrayValue(SylvaValue):
    type: MonoArrayType
    value: list


@dataclass(kw_only=True)
class MonoDynarrayType(SylvaType):
    name: str = field(default_factory=lambda: gen_name('dynarray'))
    element_type: SylvaType

    # [NOTE] Normally this would be a generic Struct, but because Sylva can't
    #        represent raw pointers we have to implement it in the compiler.

    def __post_init__(self):
        if self.element_count.value <= 0:
            raise errors.InvalidArraySize(self.location)

    def matches(self, other: SylvaType) -> bool:
        return (
            isinstance(other, MonoDynarrayType) and
            self.element_type.matches(other.element_type)
        )


@dataclass(kw_only=True)
class DynarrayType(SylvaType):
    name: str = field(default_factory=lambda: gen_name('dynarray'))

    @staticmethod
    def build_type(
        module: 'Mod',
        element_type: SylvaType,
        location: Location | None = None,
        mod: TypeModifier = TypeModifier.NoMod,
    ) -> MonoDynarrayType:
        location = location if location else Location.Generate()
        return MonoDynarrayType(
            location=location, module=module, element_type=element_type
        )


@dataclass(kw_only=True)
class DynarrayValue(SylvaValue):
    type: MonoDynarrayType
    value: list


@dataclass(kw_only=True)
class MonoStrType(MonoArrayType):
    name: str = field(init=False)
    element_type: SylvaType = field(init=False)

    def __post_init__(self):
        self.element_type = U8
        self.name = f'str{self.element_count.value}'

    def matches(self, other: SylvaType) -> bool:
        return (
            isinstance(other, MonoStrType) and
            self.element_type.matches(other.element_type)
        )


@dataclass(kw_only=True)
class StrType(ArrayType):
    name: str = field(init=False, default_factory=lambda: gen_name('str'))

    @staticmethod
    def build_type( # type: ignore
        module: 'Mod',
        element_count: IntValue,
        location: Location | None = None,
        mod: TypeModifier = TypeModifier.NoMod,
    ) -> MonoStrType:
        location = location if location else Location.Generate()
        return MonoStrType(
            location=location, module=module, element_count=element_count
        )


@dataclass(kw_only=True)
class StrValue(SylvaValue):
    type: MonoStrType
    value: bytes

    @classmethod
    def FromString(
        cls, module: 'Mod', s: str, location: Location | None = None
    ):
        location = location if location else Location.Generate()
        b = s.encode('utf-8')
        return cls(
            module=module,
            type=STR.build_type(  # type: ignore
                location=location,
                module=module,
                element_count=IntValue.FromValue(
                    location=location,
                    module=module,
                    n=len(b)
                )
            ),
            value=b
        )

    @property
    def str(self):
        return self.value.decode('utf-8')


@dataclass(kw_only=True)
class StringType(MonoDynarrayType):
    name: str = field(init=False, default_factory=lambda: gen_name('string'))
    element_type: SylvaType = field(init=False)

    def __post_init__(self):
        self.element_type = U8


@dataclass(kw_only=True)
class StringValue(SylvaValue):
    type: StringType
    value: str


@dataclass(kw_only=True)
class MonoEnumType(SylvaType):
    name: str = field(default_factory=lambda: gen_name('enum'))
    values: dict[str, SylvaValue]

    def __post_init__(self):
        if len(self.values) <= 0:
            raise errors.EmptyEnum(self.location)

        dupes = utils.get_dupes(self.values.keys())
        if dupes:
            raise errors.DuplicateFields(self, dupes)

        other_types = list(self.values.values())[1:]
        if any(not self.type.matches(v.type) for v in other_types):
            raise errors.InconsistentEnumMemberTypes(self)

    def get_attribute(self, name):
        return self.values.get(name)

    @cached_property
    def first_value(self):
        return next(iter(self.values.values()))

    @cached_property
    def type(self):
        return self.first_value.type


@dataclass(kw_only=True)
class EnumType(SylvaType):
    name: str = field(default_factory=lambda: gen_name('enum'))

    @staticmethod
    def build_type(
        module: 'Mod',
        values: dict[str, SylvaValue],
        name: str = '',
        location: Location | None = None,
        mod: TypeModifier = TypeModifier.NoMod,
    ) -> MonoEnumType:
        location = location if location else Location.Generate()
        return MonoEnumType(
            location=location, module=module, name=name, values=values
        )


@dataclass(kw_only=True)
class EnumValue(SylvaValue):
    type: MonoEnumType


@dataclass(kw_only=True)
class MonoRangeType(SylvaType):
    name: str = field(default_factory=lambda: gen_name('range'))
    min: IntValue | FloatValue | ComplexValue
    max: IntValue | FloatValue | ComplexValue

    def __post_init__(self):
        if not self.min.type.matches(self.max.type):
            raise errors.MismatchedRangeTypes(
                self.location, self.min.type, self.max.type
            )
        self.type = min.type

    def matches(self, other: SylvaType) -> bool:
        return (
            isinstance(other, MonoRangeType) and self.min == other.min and
            self.max == other.max
        )


@dataclass(kw_only=True)
class RangeType(SylvaType):
    name: str = field(default_factory=lambda: gen_name('range'))

    @staticmethod
    def build_type(
        module: 'Mod',
        min: IntValue | FloatValue | ComplexValue,
        max: IntValue | FloatValue | ComplexValue,
        name: str = '',
        location: Location | None = None,
        mod: TypeModifier = TypeModifier.NoMod,
    ) -> MonoRangeType:
        location = location if location else Location.Generate()
        return MonoRangeType(
            location=location, module=module, name=name, min=min, max=max
        )


@dataclass(kw_only=True)
class RangeValue(SylvaValue):
    type: MonoRangeType
    value: complex | float | int

    def __post_init__(self):
        if self.value < self.type.min or self.value > self.type.max:
            raise errors.InvalidRangeValue(
                self.location, self.value, self.type.min, self.type.max
            )


@dataclass(kw_only=True)
class MonoFnType(SylvaType):
    name: str = field(default_factory=lambda: gen_name('fntype'))
    mod: TypeModifier = field(init=False, default=TypeModifier.NoMod)
    parameters: list[SylvaField] = field(default_factory=list)
    return_type: SylvaType | None

    def __post_init__(self):
        if dupes := utils.get_dupes(p.name for p in self.parameters):
            raise errors.DuplicateParameters(self, dupes)
        if any(p.is_var for p in self.parameters):
            raise Exception('MonoFnType with generic params')
        if self.return_type and self.return_type.is_var:
            raise Exception('MonoFnType with generic return type')

    def matches(self, other: SylvaType) -> bool:
        return (  # yapf: ignore
            isinstance(other, MonoFnType) and
            all(
                p == op for p, op in zip(self.parameters, other.parameters)
            ) and
            (
                (self.return_type is None and other.return_type is None) or
                (self.return_type is not None and self.return_type.matches(
                    other.return_type # type: ignore
                ))
            )
        )


@dataclass(kw_only=True)
class ParamFnType(ParamSylvaType):
    name: str = field(default_factory=lambda: gen_name('fntype'))
    parameters: list[SylvaField] = field(default_factory=list)
    return_type: SylvaType | None = None
    return_type_param: SylvaField | None = None

    def __post_init__(self):
        if dupes := utils.get_dupes(p.name for p in self.parameters):
            raise errors.DuplicateParameters(self, dupes)

        if self.return_type and self.return_type_param:
            raise ValueError(
                'Cannot specify both return_type and return_type_param'
            )

        if self.return_type_param:
            generic_param_names = [p.name for p in self.parameters if p.is_var]
            if self.return_type_param.name not in generic_param_names:
                raise errors.InvalidParameterization(
                    self.location,
                    'Cannot parameterize function return type, its type '
                    f'parameter "{self.return_type_param.name}" was not found '
                    'in function parameters'
                )

    def matches(self, other: SylvaType) -> bool:
        return (  # yapf: ignore
            isinstance(other, ParamFnType) and
            all(
                p == op for p, op in zip(self.parameters, other.parameters)
            ) and
            (
                (self.return_type is None and other.return_type is None) or
                (
                    self.return_type is not None and
                    other.return_type is not None and
                    self.return_type.matches(other.return_type)
                )
            ) and
            (self.return_type_param == other.return_type_param)
        )

    @property
    def return_type_param_name(self):
        return (
            None if not self.return_type_param else self.return_type_param.name
        )

    @property
    def type_parameters(self):
        return [p.name for p in self.parameters if p.is_var]

    @property
    def return_type_must_be_inferred(self):
        return bool(self.return_type_param)

    # [TODO] Infer return type based on variable assignment when possible
    # [TODO] Monomorphizations should be unique by params/return type
    def get_or_create_monomorphization(
        self,
        module: 'Mod',
        name: str = '',
        parameters: list[SylvaField] | None = None,
        location: Location | None = None,
    ) -> MonoFnType:
        location = location if location else Location.Generate()
        parameters = parameters if parameters else []

        if len(parameters) != len(self.parameters):
            raise errors.InvalidParameterization(
                location,
                f'Expected {len(self.parameters)} parameters, got '
                f'{len(parameters)}'
            )

        type_params = {}.fromkeys(self.type_parameters)
        monomorphized_params = []
        for fn_param, given_param in zip(self.parameters, parameters):
            if fn_param.is_var:
                monomorphized_params.append(given_param)
                type_params[fn_param.name] = given_param.type  # type: ignore
            elif given_param.type != fn_param.type:
                raise errors.MismatchedTypes(
                    location, fn_param.type, given_param.type
                )
            else:
                monomorphized_params.append(fn_param)

        return MonoFnType(
            location=location,
            module=module,
            parameters=monomorphized_params,
            return_type=(  # yapf: ignore
                type_params[self.return_type_param.name]
                if self.return_type_param is not None
                else self.return_type
            )
        )


@dataclass(kw_only=True)
class FnType(SylvaType):
    name: str = field(default_factory=lambda: gen_name('fntype'))

    @staticmethod
    def build_type(
        module: 'Mod',
        name: str = '',
        parameters: list[SylvaField] | None = None,
        return_type: SylvaType | SylvaField | None = None,
        location: Location | None = None,
    ) -> MonoFnType | ParamFnType:
        location = location if location else Location.Generate()
        parameters = parameters if parameters else []
        is_param = (
            any(p.is_var for p in parameters) or
            isinstance(return_type, SylvaField)
        )

        return (
            MonoFnType(
                location=location,
                module=module,
                name=name,
                parameters=parameters,
                return_type=return_type  # type: ignore
            ) if not is_param else ParamFnType(
                location=location,
                module=module,
                name=name,
                parameters=parameters,
                return_type=(  # yapf: ignore
                    return_type
                    if not isinstance(return_type, SylvaField)
                    else None
                ),
                return_type_param=(  # yapf: ignore
                    return_type if isinstance(return_type, SylvaField) else None
                )
            )
        )


@dataclass(kw_only=True)
class FnValue(SylvaValue):
    type: MonoFnType | ParamFnType
    value: CodeBlock

    @property
    def is_var(self):
        return isinstance(self.type, ParamFnType)


@dataclass(kw_only=True)
class MonoStructType(SylvaType):
    name: str = field(default_factory=lambda: gen_name('struct'))
    fields: list[SylvaField] = field(default_factory=list)


@dataclass(kw_only=True)
class ParamStructType(ParamSylvaType):
    name: str = field(default_factory=lambda: gen_name('struct'))
    fields: list[SylvaField] = field(default_factory=list)

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

    def get_or_create_monomorphization(
        self,
        module: 'Mod',
        fields: list[SylvaField] | None = None,
        location: Location | None = None,
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
            module=module,
            fields=[f if not f.is_var else next(ifields) for f in self.fields]
        )


@dataclass(kw_only=True)
class StructType(SylvaType):
    name: str = field(default_factory=lambda: gen_name('struct'))

    @staticmethod
    def build_type(
        module: 'Mod',
        fields: list[SylvaField] | None = None,
        name: str = '',
        location: Location | None = None,
        mod: TypeModifier = TypeModifier.NoMod,
    ) -> MonoStructType | ParamStructType:
        location = location if location else Location.Generate()
        fields = fields if fields else []
        return ( # yapf: ignore
            ParamStructType(
                location=location,
                module=module,
                name=name,
                fields=fields
            )
            if any(f.is_var for f in fields)
            else MonoStructType(
                location=location,
                module=module,
                name=name,
                fields=fields
            )
        )


@dataclass(kw_only=True)
class StructValue(SylvaValue):
    type: MonoStructType
    value: dict


@dataclass(kw_only=True)
class MonoVariantType(MonoStructType):
    name: str = field(default_factory=lambda: gen_name('variant'))

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
    name: str = field(default_factory=lambda: gen_name('variant'))

    def get_or_create_monomorphization(
        self,
        module: 'Mod',
        fields: list[SylvaField] | None = None,
        location: Location | None = None,
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
            module=module,
            fields=[f if not f.is_var else next(ifields) for f in self.fields]
        )


@dataclass(kw_only=True)
class VariantType(StructType):
    name: str = field(default_factory=lambda: gen_name('variant'))

    @staticmethod
    def build_type(
        module: 'Mod',
        fields: list[SylvaField] | None = None,
        name: str = '',
        location: Location | None = None,
        mod: TypeModifier = TypeModifier.NoMod,
    ) -> MonoVariantType | ParamVariantType:
        location = location if location else Location.Generate()
        fields = fields if fields else []
        return ( # yapf: ignore
            ParamVariantType(
                location=location,
                module=module,
                name=name,
                mod=mod,
                fields=fields
            )
            if any(f.is_var for f in fields)
            else MonoVariantType(
                location=location,
                module=module,
                name=name,
                mod=mod,
                fields=fields
            )
        )


@dataclass(kw_only=True)
class VariantValue(SylvaValue):
    type: MonoVariantType
    value: dict


@dataclass(kw_only=True)
class MonoCArrayType(MonoArrayType):
    name: str = field(default_factory=lambda: gen_name('carray'))


@dataclass(kw_only=True)
class ParamCArrayType(ParamArrayType):
    name: str = field(default_factory=lambda: gen_name('carray'))

    def get_or_create_monomorphization(
        self,
        module: 'Mod',
        element_count: IntValue,
        location: Location | None = None,
    ) -> MonoCArrayType:
        location = location if location else Location.Generate()
        return MonoCArrayType(
            location=location,
            module=module,
            element_type=self.element_type,
            element_count=element_count
        )


@dataclass(kw_only=True)
class CArrayType(ArrayType):
    name: str = field(default_factory=lambda: gen_name('carray'))

    @staticmethod
    def build_type(
        module: 'Mod',
        element_type: SylvaType,
        element_count: IntValue | None,
        name: str = '',
        location: Location | None = None,
        mod: TypeModifier = TypeModifier.NoMod,
    ) -> MonoCArrayType | ParamCArrayType:
        location = location if location else Location.Generate()
        return (
            MonoCArrayType(
                location=location,
                module=module,
                name=name,
                element_type=element_type,
                element_count=element_count
            ) if element_count is not None else ParamCArrayType(
                location=location,
                module=module,
                name=name,
                element_type=element_type
            )
        )


@dataclass(kw_only=True)
class CArrayValue(SylvaValue):
    type: MonoCArrayType
    value: list


@dataclass(kw_only=True)
class MonoCBitFieldType(SylvaType):
    name: str = field(default_factory=lambda: gen_name('cbitfield'))
    bits: int
    signed: bool
    field_size: int


@dataclass(kw_only=True)
class CBitFieldType(SylvaType):
    name: str = field(default_factory=lambda: gen_name('cbitfield'))

    @staticmethod
    def build_type(
        module: 'Mod',
        bits: int,
        signed: bool,
        field_size: int,
        name: str = '',
        location: Location | None = None,
        mod: TypeModifier = TypeModifier.NoMod,
    ) -> MonoCBitFieldType:
        location = location if location else Location.Generate()
        return MonoCBitFieldType(
            location=location,
            module=module,
            name=name,
            bits=bits,
            signed=signed,
            field_size=field_size
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
class MonoCBlockFnType(SylvaType):
    name: str = field(default_factory=lambda: gen_name('cblockfn'))
    parameters: list[SylvaField] = field(default_factory=list)
    return_type: SylvaType | None

    def __post_init__(self):
        if dupes := utils.get_dupes(p.name for p in self.parameters):
            raise errors.DuplicateParameters(self, dupes)


@dataclass(kw_only=True)
class CBlockFnType(SylvaType):
    name: str = field(default_factory=lambda: gen_name('cblockfn'))

    @staticmethod
    def build_type(
        module: 'Mod',
        name: str = '',
        parameters: list[SylvaField] = field(default_factory=list),
        return_type: SylvaType | None = None,
        location: Location | None = None,
        mod: TypeModifier = TypeModifier.NoMod,
    ) -> MonoCBlockFnType:
        location = location if location else Location.Generate()
        return MonoCBlockFnType(
            location=location,
            module=module,
            name=name,
            parameters=parameters,
            return_type=return_type
        )


@dataclass(kw_only=True)
class MonoCFnType(SylvaType):
    name: str = field(default_factory=lambda: gen_name('cfn'))
    parameters: list[SylvaField] = field(default_factory=list)
    return_type: SylvaType | None

    def __post_init__(self):
        if dupes := utils.get_dupes(p.name for p in self.parameters):
            raise errors.DuplicateParameters(self, dupes)


@dataclass(kw_only=True)
class CFnType(SylvaType):
    name: str = field(default_factory=lambda: gen_name('cfn'))

    @staticmethod
    def build_type(
        module: 'Mod',
        name: str = '',
        parameters: list[SylvaField] = field(default_factory=list),
        return_type: SylvaType | None = None,
        location: Location | None = None,
        mod: TypeModifier = TypeModifier.NoMod,
    ) -> MonoCFnType:
        location = location if location else Location.Generate()
        return MonoCFnType(
            location=location,
            module=module,
            name=name,
            parameters=parameters,
            return_type=return_type
        )


@dataclass(kw_only=True)
class CFnValue(SylvaValue):
    type: MonoCFnType

    @property
    def is_var(self):
        return False


@dataclass(kw_only=True)
class MonoCPtrType(SylvaType):
    name: str = field(default_factory=lambda: gen_name('cptr'))
    referenced_type: SylvaType

    @cached_property
    def referenced_type_is_exclusive(self) -> bool:
        return self.referenced_type.mod in (
            TypeModifier.CMut, TypeModifier.ExRef, TypeModifier.Ptr
        )


@dataclass(kw_only=True)
class ParamCPtrType(ParamSylvaType):
    name: str = field(default_factory=lambda: gen_name('cptr'))

    def get_or_create_monomorphization(
        self,
        module: 'Mod',
        referenced_type: SylvaType,
        name: str = '',
        location: Location | None = None,
    ) -> MonoCPtrType:
        location = location if location else Location.Generate()
        return MonoCPtrType(
            location=location,
            module=module,
            name=name,
            referenced_type=referenced_type
        )


@dataclass(kw_only=True)
class CPtrType(SylvaType):
    name: str = field(default_factory=lambda: gen_name('cptr'))

    @staticmethod
    def build_type(
        module: 'Mod',
        referenced_type: SylvaType | None,
        name: str = '',
        location: Location | None = None,
        mod: TypeModifier = TypeModifier.NoMod,
    ) -> MonoCPtrType | ParamCPtrType:
        location = location if location else Location.Generate()

        if referenced_type is not None:
            return MonoCPtrType(
                location=location,
                module=module,
                name=name,
                mod=mod,
                referenced_type=referenced_type,
            )

        # if name is None:  # [TODO] Make this a syntax error
        #     raise errors.AnonymousGeneric(location)

        return ParamCPtrType(name=name, location=location, module=module)


@dataclass(kw_only=True)
class CPtrValue(SylvaValue):
    type: MonoCPtrType


@dataclass(kw_only=True)
class CStrType(SylvaType):
    name: str = field(default_factory=lambda: gen_name('cstr'))


@dataclass(kw_only=True)
class CStrValue(SylvaValue):
    type: CStrType
    value: str


@dataclass(kw_only=True)
class MonoCStructType(MonoStructType):
    name: str = field(default_factory=lambda: gen_name('cstruct'))
    pass


@dataclass(kw_only=True)
class CStructType(StructType):
    name: str = field(default_factory=lambda: gen_name('cstruct'))

    @staticmethod
    def build_type(
        module: 'Mod',
        fields: list[SylvaField] | None = None,
        name: str = '',
        location: Location | None = None,
        mod: TypeModifier = TypeModifier.NoMod,
    ) -> MonoCStructType:
        location = location if location else Location.Generate()
        return MonoCStructType(
            location=location,
            module=module,
            name=name,
            mod=mod,
            fields=fields if fields else []
        )


@dataclass(kw_only=True)
class CStructValue(SylvaValue):
    type: CStructType
    value: dict


@dataclass(kw_only=True)
class MonoCUnionType(MonoStructType):
    name: str = field(default_factory=lambda: gen_name('cunion'))


@dataclass(kw_only=True)
class CUnionType(SylvaType):
    name: str = field(default_factory=lambda: gen_name('cunion'))

    @staticmethod
    def build_type(
        module: 'Mod',
        fields: list[SylvaField] | None = None,
        name: str = '',
        location: Location | None = None,
        mod: TypeModifier = TypeModifier.NoMod,
    ) -> MonoCUnionType:
        location = location if location else Location.Generate()
        fields = fields if fields else []
        return MonoCUnionType(
            location=location,
            module=module,
            name=name,
            mod=mod,
            fields=fields
        )


@dataclass(kw_only=True)
class CUnionValue(SylvaValue):
    type: CUnionType
    value: dict


@dataclass(kw_only=True)
class CVoidType(SylvaType):
    name: str = field(default_factory=lambda: gen_name('cvoid'))
    is_exclusive: bool = False


@dataclass(kw_only=True)
class CVoidValue(SylvaValue):
    type: CVoidType
    value: None = None


BOOL = BoolType(module=None)  # type: ignore
RUNE = RuneType(module=None)  # type: ignore
C16 = ComplexType(module=None, bits=16)  # type: ignore
C32 = ComplexType(module=None, bits=32)  # type: ignore
C64 = ComplexType(module=None, bits=64)  # type: ignore
C128 = ComplexType(module=None, bits=128)  # type: ignore
F16 = FloatType(module=None, bits=16)  # type: ignore
F32 = FloatType(module=None, bits=32)  # type: ignore
F64 = FloatType(module=None, bits=64)  # type: ignore
F128 = FloatType(module=None, bits=128)  # type: ignore
I8 = IntType(module=None, bits=8, signed=True)  # type: ignore
I16 = IntType(module=None, bits=16, signed=True)  # type: ignore
I32 = IntType(module=None, bits=32, signed=True)  # type: ignore
I64 = IntType(module=None, bits=64, signed=True)  # type: ignore
I128 = IntType(module=None, bits=128, signed=True)  # type: ignore
U8 = IntType(module=None, bits=8, signed=False)  # type: ignore
U16 = IntType(module=None, bits=16, signed=False)  # type: ignore
U32 = IntType(module=None, bits=32, signed=False)  # type: ignore
U64 = IntType(module=None, bits=64, signed=False)  # type: ignore
U128 = IntType(module=None, bits=128, signed=False)  # type: ignore
ARRAY = ArrayType(module=None)  # type: ignore
DYNARRAY = DynarrayType(module=None)  # type: ignore
STR = StrType(module=None)  # type: ignore
STRING = StringType(module=None)  # type: ignore
ENUM = EnumType(module=None)  # type: ignore
RANGE = RangeType(module=None)  # type: ignore
FN = FnType(module=None)  # type: ignore
STRUCT = StructType(module=None)  # type: ignore
TYPE = Type(module=None)  # type: ignore
VARIANT = VariantType(module=None)  # type: ignore

CARRAY = CArrayType(module=None)  # type: ignore
CBITFIELD = CBitFieldType(module=None)  # type: ignore
CBLOCKFN = CBlockFnType(module=None)  # type: ignore
CFN = CFnType(module=None)  # type: ignore
CPTR = CPtrType(module=None)  # type: ignore
CSTR = CStrType(  # type: ignore
    module=None  # type: ignore
)  # [NOTE] Should this also inherit from CARRAY or w/e?  # type: ignore
CSTRUCT = CStructType(module=None)  # type: ignore
CUNION = CUnionType(module=None)  # type: ignore
CVOID = CVoidType(module=None)  # type: ignore
CVOIDEX = CVoidType(module=None, is_exclusive=True)  # type: ignore


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
class TypeDef(NamedSylvaObject):
    type: SylvaType
    c_compiler_builtin: bool = field(default=False)

    def __post_init__(self):
        if not self.type.name:
            self.type.name = self.name


@dataclass(kw_only=True)
class SelfReferentialField(NamedSylvaObject):
    name: str

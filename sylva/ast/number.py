from dataclasses import dataclass
from functools import cached_property
from typing import Union

from sylva.ast.expr import Expr, LiteralExpr
from sylva.ast.sylva_type import SylvaType


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
        return f'c{self.bits}'


@dataclass(kw_only=True)
class FloatType(SizedNumericType):

    @cached_property
    def mname(self) -> str:
        return f'f{self.bits}'


@dataclass(kw_only=True)
class IntType(SizedNumericType):
    signed: bool

    @cached_property
    def mname(self) -> str:
        return f'{"i" if self.signed else "u"}{self.bits}'


@dataclass(kw_only=True)
class NumericLiteralExpr(LiteralExpr):
    type: Union[ComplexType, FloatType, IntType]


@dataclass(kw_only=True)
class IntExpr(Expr):
    type: IntType


@dataclass(kw_only=True)
class IntLiteralExpr(NumericLiteralExpr):

    @classmethod
    def FromRawValue(cls, location, raw_value):
        from .type_singleton import get_int_type

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
            raise ValueError('Int missing signedness and/or size')

        return NumericLiteralExpr( # pylint: disable=too-many-function-args
            get_int_type(bits=size, signed=signed),
            value,
            location=location,
        )

    @property
    def signed(self):
        return self.type.signed

    @property
    def size(self):
        return self.type.bits


class FloatLiteralExpr(NumericLiteralExpr):

    @classmethod
    def FromRawValue(cls, location, raw_value):
        from .type_singleton import get_float_type

        val = float(raw_value[:-3])

        # pylint: disable=too-many-function-args
        if raw_value.endswith('f16'):
            return cls(get_float_type(16), val, location=location)
        if raw_value.endswith('f32'):
            return cls(get_float_type(32), val, location=location)
        if raw_value.endswith('f64'):
            return cls(get_float_type(64), val, location=location)
        if raw_value.endswith('f128'):
            return cls(get_float_type(128), val, location=location)
        raise Exception(f'Malformed float value {raw_value}')

    @property
    def size(self):
        return self.type.bits


class ComplexLiteralExpr(NumericLiteralExpr):

    @classmethod
    def FromRawValue(cls, location, raw_value):
        from .type_singleton import get_complex_type

        val = complex(raw_value[:-3])

        # pylint: disable=too-many-function-args
        if raw_value.endswith('f16'):
            return cls(get_complex_type(16), val, location=location)
        if raw_value.endswith('f32'):
            return cls(get_complex_type(32), val, location=location)
        if raw_value.endswith('f64'):
            return cls(get_complex_type(64), val, location=location)
        if raw_value.endswith('f128'):
            return cls(get_complex_type(128), val, location=location)
        raise Exception(f'Malformed complex value {raw_value}')

    @property
    def size(self):
        return self.type.bits

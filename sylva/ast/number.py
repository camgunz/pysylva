from functools import cached_property

from llvmlite import ir

from attrs import define, field

from .. import _SIZE_SIZE, utils
from ..location import Location
from .expr import LiteralExpr, ValueExpr
from .sylva_type import SylvaType


@define(eq=False, slots=True)
class NumericType(SylvaType):
    pass


@define(eq=False, slots=True)
class SizedNumericType(NumericType):
    bits = field()


@define(eq=False, slots=True)
class ComplexType(SizedNumericType):

    @cached_property
    def mname(self):
        return utils.mangle(['c', self.bits])

    def get_value_expr(self, location):
        return ComplexExpr(location=location, type=self)

    @llvm_type.default # noqa: F821
    def _llvm_type_factory(self):
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


@define(eq=False, slots=True)
class FloatType(SizedNumericType):

    @cached_property
    def mname(self):
        return utils.mangle(['f', self.bits])

    def get_value_expr(self, location):
        return FloatExpr(location=location, type=self)

    @llvm_type.default # noqa: F821
    def _llvm_type_factory(self):
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


@define(eq=False, slots=True)
class IntType(SizedNumericType):
    signed = field()

    @cached_property
    def mname(self):
        return utils.mangle(['i' if self.signed else 'u', self.bits])

    @classmethod
    def SmallestThatHolds(cls, x):
        return cls(Location.Generate(), utils.smallest_uint(x), signed=False)

    @classmethod
    def Platform(cls, signed):
        return cls(Location.Generate(), bits=_SIZE_SIZE, signed=signed)

    def get_value_expr(self, location):
        return IntExpr(location=location, type=self)

    @llvm_type.default # noqa: F821
    def _llvm_type_factory(self):
        return ir.IntType(self.bits)


@define(eq=False, slots=True)
class NumericLiteralExpr(LiteralExpr):
    pass


@define(eq=False, slots=True)
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

        return cls(
            location=location,
            type=get_int_type(bits=size, signed=signed),
            value=value
        )

    @property
    def signed(self):
        return self.type.signed

    @property
    def size(self):
        return self.type.bits


@define(eq=False, slots=True)
class IntExpr(ValueExpr):
    pass


@define(eq=False, slots=True)
class FloatLiteralExpr(NumericLiteralExpr):

    @classmethod
    def FromRawValue(cls, location, raw_value):
        from .type_singleton import get_float_type

        if raw_value.endswith('f16'):
            return cls(location, get_float_type(16), float(raw_value[:-3]))
        if raw_value.endswith('f32'):
            return cls(location, get_float_type(32), float(raw_value[:-3]))
        if raw_value.endswith('f64'):
            return cls(location, get_float_type(64), float(raw_value[:-3]))
        if raw_value.endswith('f128'):
            return cls(location, get_float_type(128), float(raw_value[:-4]))
        raise Exception(f'Malformed float value {raw_value}')

    @property
    def size(self):
        return self.type.bits


@define(eq=False, slots=True)
class FloatExpr(ValueExpr):
    pass


@define(eq=False, slots=True)
class ComplexLiteralExpr(NumericLiteralExpr):

    @classmethod
    def FromRawValue(cls, location, raw_value):
        from .type_singleton import get_complex_type

        if raw_value.endswith('f16'):
            return cls(location, get_complex_type(16), complex(raw_value[:-3]))
        if raw_value.endswith('f32'):
            return cls(location, get_complex_type(32), complex(raw_value[:-3]))
        if raw_value.endswith('f64'):
            return cls(location, get_complex_type(64), complex(raw_value[:-3]))
        if raw_value.endswith('f128'):
            return cls(
                location, get_complex_type(128), complex(raw_value[:-4])
            )
        raise Exception(f'Malformed complex value {raw_value}')

    @property
    def size(self):
        return self.type.bits


@define(eq=False, slots=True)
class ComplexExpr(ValueExpr):
    pass

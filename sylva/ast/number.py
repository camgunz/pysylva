import typing

from llvmlite import ir # type: ignore

from attrs import define

from .expr import LiteralExpr, ValueExpr
from .sylva_type import LLVMTypeMixIn, SylvaType
from .. import _SIZE_SIZE, utils
from ..location import Location


@define(eq=False, slots=True)
class NumericType(SylvaType, LLVMTypeMixIn):
    pass


@define(eq=False, slots=True)
class SizedNumericType(NumericType):
    bits: int
    implementations: typing.List = []


@define(eq=False, slots=True)
class ComplexType(SizedNumericType):

    def mangle(self):
        base = f'c{self.bits}'
        return f'{len(base)}{base}'

    def get_value_expr(self, location):
        return ComplexExpr(location=location, type=self)

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


@define(eq=False, slots=True)
class FloatType(SizedNumericType):

    def mangle(self):
        base = f'f{self.bits}'
        return f'{len(base)}{base}'

    def get_value_expr(self, location):
        return FloatExpr(location=location, type=self)

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


@define(eq=False, slots=True)
class IntegerType(SizedNumericType):
    signed: bool
    implementations: typing.List = []

    def mangle(self):
        prefix = 'i' if self.signed else 'u'
        base = f'{prefix}{self.bits}'
        return f'{len(base)}{base}'

    @classmethod
    def SmallestThatHolds(cls, x):
        return cls(Location.Generate(), utils.smallest_uint(x), signed=False)

    @classmethod
    def Platform(cls, signed):
        return cls(Location.Generate(), bits=_SIZE_SIZE, signed=signed)

    def get_value_expr(self, location):
        return IntegerExpr(location=location, type=self)

    def get_llvm_type(self, module):
        return ir.IntType(self.bits)


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
            raise ValueError('Integer missing signedness and/or size')

        return cls(
            location=location,
            type=IntegerType(location=location, bits=size, signed=signed),
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

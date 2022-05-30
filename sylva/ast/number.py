from functools import cached_property

from llvmlite import ir

from .. import utils
from .literal import LiteralExpr
from .sylva_type import SylvaType


class NumericType(SylvaType):
    pass


class SizedNumericType(NumericType):

    def __init__(self, location, bits):
        NumericType.__init__(self, location)
        self.bits = bits


class ComplexType(SizedNumericType):

    def __init__(self, location, bits):
        SizedNumericType.__init__(self, location, bits)
        if self.bits == 8:
            self.llvm_type = ir.HalfType()
        if self.bits == 16:
            self.llvm_type = ir.FloatType()
        if self.bits == 32:
            self.llvm_type = ir.DoubleType()
        # [NOTE] llvmlite won't do float types > 64 bits
        if self.bits == 64:
            self.llvm_type = ir.DoubleType()
        if self.bits == 128:
            self.llvm_type = ir.DoubleType()

    @cached_property
    def mname(self):
        return f'c{self.bits}'


class FloatType(SizedNumericType):

    def __init__(self, location, bits):
        SizedNumericType.__init__(self, location, bits)
        # [NOTE] llvmlite won't do float types < 16 bits
        if self.bits == 8:
            self.llvm_type = ir.HalfType()
        if self.bits == 16:
            self.llvm_type = ir.HalfType()
        if self.bits == 32:
            self.llvm_type = ir.FloatType()
        if self.bits == 64:
            self.llvm_type = ir.DoubleType()
        # [NOTE] llvmlite won't do float types > 64 bits
        if self.bits == 128:
            self.llvm_type = ir.DoubleType()

    @cached_property
    def mname(self):
        return f'f{self.bits}'


class IntType(SizedNumericType):

    def __init__(self, location, bits, signed):
        SizedNumericType.__init__(self, location, bits)
        self.signed = signed
        self.llvm_type = ir.IntType(self.bits)

    @cached_property
    def mname(self):
        return f'{"i" if self.signed else "u"}{self.bits}'


class NumericLiteralExpr(LiteralExpr):
    pass


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

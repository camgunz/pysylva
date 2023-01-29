import enum

from functools import cache

from .. import _SIZE_SIZE, errors
from ..location import Location
from .array import ArrayType
from .bool import BoolType
from .carray import CArrayType
from .cptr import CPtrType
from .cstr import CStrType
from .cvoid import CVoidType
from .cunion import CUnionType
from .dynarray import DynarrayType
from .iface import IfaceType
from .fn import MonoFnType
from .number import ComplexType, FloatType, IntType
from .pointer import PointerType
from .rune import RuneType
from .str import StrType
from .string import StringType
from .struct import StructType
from .variant import VariantType


class TypeSingletonsBuilder:

    @cache
    def __getattr__(self, name):
        if name == 'C16':
            return ComplexType(name='c16', bits=16)

        if name == 'C32':
            return ComplexType(name='c32', bits=32)

        if name == 'C64':
            return ComplexType(name='c64', bits=64)

        if name == 'C128':
            return ComplexType(name='c128', bits=128)

        if name == 'F16':
            return FloatType(name='f16', bits=16)

        if name == 'F32':
            return FloatType(name='f32', bits=32)

        if name == 'F64':
            return FloatType(name='f64', bits=64)

        if name == 'F128':
            return FloatType(name='f128', bits=128)

        if name == 'I8':
            return IntType(name='i8', bits=8, signed=True)

        if name == 'I16':
            return IntType(name='i16', bits=16, signed=True)

        if name == 'I32':
            return IntType(name='i32', bits=32, signed=True)

        if name == 'I64':
            return IntType(name='i64', bits=64, signed=True)

        if name == 'I128':
            return IntType(name='i128', bits=128, signed=True)

        if name == 'INT':
            if _SIZE_SIZE == 8:
                return self.I8
            if _SIZE_SIZE == 16:
                return self.I16
            if _SIZE_SIZE == 32:
                return self.I32
            if _SIZE_SIZE == 64:
                return self.I64
            if _SIZE_SIZE == 128:
                return self.I128

            raise errors.UnsupportedPlatformIntegerSize(_SIZE_SIZE)

        if name == 'U8':
            return IntType(name='u8', bits=8, signed=False)

        if name == 'U16':
            return IntType(name='u16', bits=16, signed=False)

        if name == 'U32':
            return IntType(name='u32', bits=32, signed=False)

        if name == 'U64':
            return IntType(name='u64', bits=64, signed=False)

        if name == 'U128':
            return IntType(name='u128', bits=128, signed=False)

        if name == 'UINT':
            if _SIZE_SIZE == 8:
                return self.U8
            if _SIZE_SIZE == 16:
                return self.U16
            if _SIZE_SIZE == 32:
                return self.U32
            if _SIZE_SIZE == 64:
                return self.U64
            if _SIZE_SIZE == 128:
                return self.U128

            raise errors.UnsupportedPlatformIntegerSize(_SIZE_SIZE)

        if name == 'BOOL':
            return BoolType()

        if name == 'RUNE':
            return RuneType()

        if name == 'STRING':
            return StringType()

        if name == 'CPTR':
            return CPtrType()

        if name == 'CSTR':
            return CStrType()

        if name == 'CVOID':
            return CVoidType()

        if name == 'CARRAY':
            return CArrayType()

        # if name == 'CUNION':
        #     return CUnionType(location=Location.Generate())

        if name == 'ARRAY':
            return ArrayType()

        if name == 'DYNARRAY':
            return DynarrayType()

        if name == 'POINTER':
            return PointerType()

        if name == 'STR':
            return StrType()

        # if name == 'STRUCT':
        #     return StructType(location=Location.Generate())

        # if name == 'VARIANT':
        #     return VariantType(location=Location.Generate())

        raise AttributeError(
            f"'TypeSingletons' object has no attribute '{name}"
        )


TypeSingletons = TypeSingletonsBuilder()


class IfaceSingletons(enum.Enum):
    ARRAY = IfaceType(
        location=Location.Generate(),
        functions={
            'get_length':
                MonoFnType(
                    location=Location.Generate(),
                    parameters=[],
                    return_type=TypeSingletons.UINT, # type: ignore
                )
        }
    )
    STRING = IfaceType(
        location=Location.Generate(),
        functions={
            'get_length':
                MonoFnType(
                    location=Location.Generate(),
                    parameters=[],
                    return_type=TypeSingletons.UINT, # type: ignore
                )
        }
    )


def get_int_type(bits, signed):
    if bits == 8:
        return TypeSingletons.I8 if signed else TypeSingletons.U8
    if bits == 16:
        return TypeSingletons.I16 if signed else TypeSingletons.U16
    if bits == 32:
        return TypeSingletons.I32 if signed else TypeSingletons.U32
    if bits == 64:
        return TypeSingletons.I64 if signed else TypeSingletons.U64
    if bits == 'platform':
        return TypeSingletons.INT if signed else TypeSingletons.UINT
    raise ValueError(f'Invalid bits value {bits}')


def get_signed_int_types():
    return [
        TypeSingletons.I8,
        TypeSingletons.I16,
        TypeSingletons.I32,
        TypeSingletons.I64,
        TypeSingletons.I128
    ]


def get_unsigned_int_types():
    return [
        TypeSingletons.U8,
        TypeSingletons.U16,
        TypeSingletons.U32,
        TypeSingletons.U64,
        TypeSingletons.U128
    ]


def get_float_type(bits):
    if bits == 16:
        return TypeSingletons.F16
    if bits == 32:
        return TypeSingletons.F32
    if bits == 64:
        return TypeSingletons.F64
    raise ValueError(f'Invalid bits value {bits}')


def get_complex_type(bits):
    if bits == 16:
        return TypeSingletons.C16
    if bits == 32:
        return TypeSingletons.C32
    if bits == 64:
        return TypeSingletons.C64
    if bits == 128:
        return TypeSingletons.C128
    raise ValueError(f'Invalid bits value {bits}')

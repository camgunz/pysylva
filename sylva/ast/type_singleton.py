import enum

from .. import _SIZE_SIZE
from ..location import Location
from .bool import BoolType
from .cstr import CStrType
from .rune import RuneType
from .number import ComplexType, FloatType, IntType


class TypeSingletons(enum.Enum):
    BOOL = BoolType(location=Location.Generate())
    C16 = ComplexType(location=Location.Generate(), bits=16)
    C32 = ComplexType(location=Location.Generate(), bits=32)
    C64 = ComplexType(location=Location.Generate(), bits=64)
    C128 = ComplexType(location=Location.Generate(), bits=128)
    F16 = FloatType(location=Location.Generate(), bits=16)
    F32 = FloatType(location=Location.Generate(), bits=32)
    F64 = FloatType(location=Location.Generate(), bits=64)
    F128 = FloatType(location=Location.Generate(), bits=128)
    INT = IntType(location=Location.Generate(), bits=_SIZE_SIZE, signed=True)
    I8 = IntType(location=Location.Generate(), bits=8, signed=True)
    I16 = IntType(location=Location.Generate(), bits=16, signed=True)
    I32 = IntType(location=Location.Generate(), bits=32, signed=True)
    I64 = IntType(location=Location.Generate(), bits=64, signed=True)
    I128 = IntType(location=Location.Generate(), bits=128, signed=True)
    RUNE = RuneType(location=Location.Generate())
    UINT = IntType(location=Location.Generate(), bits=_SIZE_SIZE, signed=False)
    U8 = IntType(location=Location.Generate(), bits=8, signed=False)
    U16 = IntType(location=Location.Generate(), bits=16, signed=False)
    U32 = IntType(location=Location.Generate(), bits=32, signed=False)
    U64 = IntType(location=Location.Generate(), bits=64, signed=False)
    U128 = IntType(location=Location.Generate(), bits=128, signed=False)
    CSTR = CStrType(location=Location.Generate())
    CVOID = IntType(location=Location.Generate(), bits=8, signed=True)


def get_int_type(bits, signed):
    if bits == 8:
        return TypeSingletons.I8.value if signed else TypeSingletons.U8.value
    if bits == 16:
        return TypeSingletons.I16.value if signed else TypeSingletons.U16.value
    if bits == 32:
        return TypeSingletons.I32.value if signed else TypeSingletons.U32.value
    if bits == 64:
        return TypeSingletons.I64.value if signed else TypeSingletons.U64.value
    if bits == 'platform':
        return (
            TypeSingletons.INT.value if signed else TypeSingletons.UINT.value
        )
    raise ValueError(f'Invalid bits value {bits}')


def get_float_type(bits):
    if bits == 16:
        return TypeSingletons.F16.value
    if bits == 32:
        return TypeSingletons.F32.value
    if bits == 64:
        return TypeSingletons.F64.value
    raise ValueError(f'Invalid bits value {bits}')


def get_complex_type(bits):
    if bits == 16:
        return TypeSingletons.C16.value
    if bits == 32:
        return TypeSingletons.C32.value
    if bits == 64:
        return TypeSingletons.C64.value
    if bits == 128:
        return TypeSingletons.C128.value
    raise ValueError(f'Invalid bits value {bits}')

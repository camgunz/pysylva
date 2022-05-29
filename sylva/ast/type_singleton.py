import enum

from .. import _SIZE_SIZE
from ..location import Location
from .attribute import Attribute
from .array import ArrayType
from .bool import BoolType
from .carray import CArrayType
from .cptr import CPtrType
from .cstr import CStrType
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


class TypeSingletons(enum.Enum):
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
    UINT = IntType(location=Location.Generate(), bits=_SIZE_SIZE, signed=False)
    U8 = IntType(location=Location.Generate(), bits=8, signed=False)
    U16 = IntType(location=Location.Generate(), bits=16, signed=False)
    U32 = IntType(location=Location.Generate(), bits=32, signed=False)
    U64 = IntType(location=Location.Generate(), bits=64, signed=False)
    U128 = IntType(location=Location.Generate(), bits=128, signed=False)
    BOOL = BoolType(location=Location.Generate())
    RUNE = RuneType(location=Location.Generate())
    STRING = StringType(location=Location.Generate())
    CPTR = CPtrType(location=Location.Generate())
    CSTR = CStrType(location=Location.Generate())
    CVOID = IntType(location=Location.Generate(), bits=8, signed=True)
    CARRAY = CArrayType(location=Location.Generate())
    CUNION = CUnionType(location=Location.Generate())
    ARRAY = ArrayType(location=Location.Generate())
    DYNARRAY = DynarrayType(location=Location.Generate())
    POINTER = PointerType(location=Location.Generate())
    STR = StrType(location=Location.Generate())
    STRUCT = StructType(location=Location.Generate())
    VARIANT = VariantType(location=Location.Generate())


class IfaceSingletons(enum.Enum):
    ARRAY = IfaceType(
        location=Location.Generate(),
        functions=[
            Attribute(
                location=Location.Generate(),
                name='get_length',
                type=MonoFnType(
                    location=Location.Generate(),
                    parameters=[],
                    return_type=TypeSingletons.UINT.value,
                )
            )
        ]
    )
    STRING = IfaceType(
        location=Location.Generate(),
        functions=[
            Attribute(
                location=Location.Generate(),
                name='get_length',
                type=MonoFnType(
                    location=Location.Generate(),
                    parameters=[],
                    return_type=TypeSingletons.UINT.value,
                )
            )
        ]
    )


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

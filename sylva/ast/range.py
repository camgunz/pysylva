import typing

from attrs import define

from .number import NumericType
from .operator import AttributeLookupMixIn
from .sylva_type import LLVMTypeMixIn, SylvaType


@define(eq=False, slots=True)
class RangeType(SylvaType, LLVMTypeMixIn, AttributeLookupMixIn):
    type: NumericType
    min: int
    max: int
    implementations: typing.List = []

    def mangle(self):
        return self.type.mangle()

    def get_llvm_type(self, module):
        return self.type.type

import typing

from attrs import define, field

from .attribute_lookup import AttributeLookupMixIn
from .number import NumericType
from .sylva_type import SylvaType


@define(eq=False, slots=True)
class RangeType(SylvaType, AttributeLookupMixIn):
    type: NumericType
    min: int
    max: int
    llvm_type = field(init=False)
    implementations: typing.List = []

    def mangle(self):
        return self.type.mangle()

    @llvm_type.default
    def _llvm_type_factory(self):
        return self.type.llvm_type

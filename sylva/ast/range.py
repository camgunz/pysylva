from functools import cached_property

from attrs import define, field

from .attribute_lookup import AttributeLookupMixIn
from .sylva_type import SylvaType


@define(eq=False, slots=True)
class RangeType(SylvaType, AttributeLookupMixIn):
    min = field()
    max = field()

    @cached_property
    def mname(self):
        return self.type.mname

    @llvm_type.default # noqa: F821
    def _llvm_type_factory(self):
        return self.type.llvm_type

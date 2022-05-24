from functools import cached_property

from attrs import define, field
from llvmlite import ir

from .. import utils
from .sylva_type import SylvaType


@define(eq=False, slots=True)
class CBitFieldType(SylvaType):
    bits = field()
    signed = field()
    field_size = field()

    @llvm_type.default # noqa: F821
    def _llvm_type_factory(self):
        return ir.IntType(self.bits)

    @cached_property
    def mname(self):
        return utils.mangle(['cbf', self.bits, self.signed, self.field_size])

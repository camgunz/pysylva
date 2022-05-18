import typing

from attrs import define
from llvmlite import ir # type: ignore

from .sylva_type import LLVMTypeMixIn, SylvaType


@define(eq=False, slots=True)
class CBitFieldType(SylvaType, LLVMTypeMixIn):
    bits: int
    signed: bool
    field_size: int
    implementations: typing.List = []

    # pylint: disable=unused-argument
    def get_llvm_type(self, module):
        return ir.IntType(self.bits)

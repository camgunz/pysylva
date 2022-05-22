import typing

from attrs import define, field
from llvmlite import ir # type: ignore

from .sylva_type import SylvaType


@define(eq=False, slots=True)
class CBitFieldType(SylvaType):
    bits: int
    signed: bool
    field_size: int
    implementations: typing.List = []
    llvm_type = field(init=False)

    @llvm_type.default
    def _llvm_type_factory(self):
        return ir.IntType(self.bits)

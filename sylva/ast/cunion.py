from attrs import define, field
from llvmlite import ir # type: ignore

from .defs import SelfReferentialDef
from .union import BaseUnionType


@define(eq=False, slots=True)
class CUnionType(BaseUnionType):
    llvm_type = field(init=False)

    @llvm_type.default
    def _llvm_type_factory(self):
        return ir.LiteralStructType([self.get_largest_field()])


@define(eq=False, slots=True)
class CUnionDef(SelfReferentialDef):
    llvm_value: None | ir.Value = None

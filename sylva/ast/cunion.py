from attrs import define
from llvmlite import ir # type: ignore

from .defs import Def, LLVMDefMixIn
from .union import BaseUnionType


@define(eq=False, slots=True)
class CUnionType(BaseUnionType):

    def get_llvm_type(self, module):
        return ir.LiteralStructType([self.get_largest_field(module)])


@define(eq=False, slots=True)
class CUnionDef(Def, LLVMDefMixIn):
    llvm_value: None | ir.Value = None

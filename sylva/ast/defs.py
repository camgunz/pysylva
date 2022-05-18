from attrs import define, field
from llvmlite import ir # type: ignore

from .base import Node
from .cfunction import CFunctionType
from .sylva_type import LLVMTypeMixIn


@define(eq=False, slots=True)
class Def(Node):
    name: str
    type = field()


@define(eq=False, slots=True)
class CFunction(Def):
    type: CFunctionType
    llvm_value: None | ir.Function = None


@define(eq=False, slots=True)
class LLVMDefMixIn:
    type: LLVMTypeMixIn

    def get_llvm_type(self, module):
        return self.type.get_llvm_type(module)


@define(eq=False, slots=True)
class ParamLLVMDefMixIn(LLVMDefMixIn):

    # pylint: disable=arguments-differ
    def get_llvm_type(self, module, index):
        return self.type.monomorphizations[index].get_llvm_type(module)


@define(eq=False, slots=True)
class CArray(Def, LLVMDefMixIn):
    pass


@define(eq=False, slots=True)
class Variant(Def, ParamLLVMDefMixIn):
    pass


@define(eq=False, slots=True)
class CUnion(Def, LLVMDefMixIn):
    llvm_value: None | ir.Value = None

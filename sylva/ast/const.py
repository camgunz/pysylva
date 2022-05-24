from attrs import define, field
from llvmlite import ir

from .defs import Def


@define(eq=False, slots=True)
class ConstDef(Def):
    value = field()

    def llvm_define(self, llvm_module):
        const = ir.GlobalVariable(llvm_module, self.type.llvm_type, self.name)
        const.initializer = ir.Constant(
            self.type.llvm_type, self.value.emit(llvm_module, None, None)
        )
        const.global_constant = True
        return const

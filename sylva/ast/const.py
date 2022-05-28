from llvmlite import ir

from .defs import BaseDef


class ConstDef(BaseDef):

    def __init__(self, location, name, value):
        BaseDef.__init__(self, location, name, value.type)
        self.value = value

    def llvm_define(self, llvm_module):
        const = ir.GlobalVariable(llvm_module, self.type.llvm_type, self.name)
        const.initializer = ir.Constant(
            self.type.llvm_type, self.value.emit(llvm_module, None, None)
        )
        const.global_constant = True
        return const

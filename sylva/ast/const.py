from llvmlite import ir

from .defs import BaseDef


class Const(BaseDef):

    def __init__(self, location, name, value):
        BaseDef.__init__(self, location, name, value.type)
        self.value = value

    def emit(self, obj, module, builder, scope, name):
        llvm_module = module.type.llvm_type
        const = ir.GlobalVariable(llvm_module, self.type.llvm_type, self.name)
        const.initializer = self.value.emit(obj, module, builder, scope, name)
        # const.initializer = ir.Constant(
        #     self.type.llvm_type,
        #     self.value.emit(obj, module, builder, scope, name)
        # )
        const.global_constant = True
        return const

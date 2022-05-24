from attrs import define
from llvmlite import ir # type: ignore

from .defs import Def
from .expr import LiteralExpr
from .sylva_type import SylvaType


@define(eq=False, slots=True)
class ConstDef(Def):
    type: SylvaType
    value: LiteralExpr

    def llvm_define(self, llvm_module):
        const = ir.GlobalVariable(llvm_module, self.type.llvm_type, self.name)
        const.initializer = ir.Constant(
            self.type.llvm_type, self.value.emit(llvm_module, None, None)
        )
        const.global_constant = True
        return const

from attrs import define
from llvmlite import ir # type: ignore

from .defs import Def
from .expr import LiteralExpr
from .sylva_type import SylvaType


@define(eq=False, slots=True)
class ConstDef(Def):
    type: SylvaType
    value: LiteralExpr
    llvm_value: None | ir.Value = None

    def get_llvm_value(self, module):
        return self.value.get_llvm_value(module)

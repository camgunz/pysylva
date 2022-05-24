from functools import cached_property

from attrs import define
from llvmlite import ir

from .defs import SelfReferentialTypeDef
from .union import BaseUnionType


@define(eq=False, slots=True)
class CUnionType(BaseUnionType):

    @llvm_type.default # noqa: F821
    def _llvm_type_factory(self):
        return ir.LiteralStructType([self.get_largest_field()])

    @cached_property
    def mname(self):
        return ''.join(['6cunion', ''.join(f.type.mname for f in self.fields)])


@define(eq=False, slots=True)
class CUnionDef(SelfReferentialTypeDef):
    pass

from functools import cached_property

from attrs import define, field
from llvmlite import ir # type: ignore

from .defs import SelfReferentialTypeDef
from .union import BaseUnionType


@define(eq=False, slots=True)
class CUnionType(BaseUnionType):
    llvm_type = field(init=False)

    @llvm_type.default
    def _llvm_type_factory(self):
        return ir.LiteralStructType([self.get_largest_field()])

    @cached_property
    def mname(self):
        # pylint: disable=not-an-iterable
        return ''.join(['6cunion', ''.join(f.type.mname for f in self.fields)])


@define(eq=False, slots=True)
class CUnionDef(SelfReferentialTypeDef):
    pass

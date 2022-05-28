from functools import cached_property

from llvmlite import ir

from .defs import SelfReferentialTypeDef
from .union import BaseUnionType


class CUnionType(BaseUnionType):

    def __init__(self, location, fields):
        BaseUnionType.__init__(self, location, fields)
        self.llvm_type = ir.LiteralStructType([self.get_largest_field()])

    @cached_property
    def mname(self):
        return ''.join(['6cunion', ''.join(f.type.mname for f in self.fields)])


class CUnionDef(SelfReferentialTypeDef):
    pass

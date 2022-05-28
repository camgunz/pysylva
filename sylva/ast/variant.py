from functools import cached_property

from llvmlite import ir

from .. import utils
from .defs import SelfReferentialParamTypeDef
from .sylva_type import SylvaParamType
from .union import BaseUnionType


class MonoVariantType(BaseUnionType):

    def __init__(self, location, fields):
        BaseUnionType.__init__(self, location, fields)
        self.llvm_type = ir.LiteralStructType([
            self.get_largest_field(),
            ir.IntType(utils.round_up_to_multiple(len(self.fields), 8))
        ])

    def get_attribute(self, location, name):
        for f in self.fields:
            if f.name == name:
                return f

    @cached_property
    def mname(self):
        return ''.join([
            '7variant', ''.join(f.type.mname for f in self.fields)
        ])


class VariantType(SylvaParamType):
    pass


class VariantDef(SelfReferentialParamTypeDef):

    def llvm_define(self, llvm_module):
        pass

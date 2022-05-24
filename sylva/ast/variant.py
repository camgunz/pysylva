from functools import cached_property

from attrs import define
from llvmlite import ir

from .. import utils
from .attribute_lookup import AttributeLookupMixIn
from .defs import SelfReferentialParamTypeDef
from .sylva_type import SylvaParamType
from .union import BaseUnionType


@define(eq=False, slots=True)
class MonoVariantType(BaseUnionType, AttributeLookupMixIn):

    def get_attribute(self, location, name):
        for f in self.fields:
            if f.name == name:
                return f

    @llvm_type.default # noqa: F821
    def _llvm_type_factory(self):
        tag_bit_width = utils.round_up_to_multiple(len(self.fields), 8)
        return ir.LiteralStructType([
            self.get_largest_field(), ir.IntType(tag_bit_width)
        ])

    @cached_property
    def mname(self):
        return ''.join([
            '7variant', ''.join(f.type.mname for f in self.fields)
        ])


@define(eq=False, slots=True)
class VariantType(SylvaParamType):
    pass


@define(eq=False, slots=True)
class VariantDef(SelfReferentialParamTypeDef):

    def llvm_define(self, llvm_module):
        pass

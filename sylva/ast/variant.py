import typing

from attrs import define
from llvmlite import ir # type: ignore

from .. import utils
from .defs import Def, ParamLLVMDefMixIn
from .operator import AttributeLookupMixIn
from .sylva_type import ParamTypeMixIn, SylvaType
from .union import BaseUnionType
from .type_mapping import Field


@define(eq=False, slots=True)
class MonoVariantType(BaseUnionType, AttributeLookupMixIn):
    name: str
    fields: typing.List[Field] = []
    implementations: typing.List = []

    # pylint: disable=unused-argument
    def get_attribute(self, location, name):
        for f in self.fields:
            if f.name == name:
                return f

    def get_llvm_type(self, module):
        tag_bit_width = utils.round_up_to_multiple(len(self.fields), 8)
        return ir.LiteralStructType([
            self.get_largest_field(module), ir.IntType(tag_bit_width)
        ])


@define(eq=False, slots=True)
class VariantType(SylvaType, ParamTypeMixIn):
    name: str
    monomorphizations: typing.List[MonoVariantType] = []
    implementations: typing.List = []


@define(eq=False, slots=True)
class VariantDef(Def, ParamLLVMDefMixIn):
    pass

from functools import cached_property

from llvmlite import ir

from .. import utils
from .sylva_type import SylvaParamType
from .union import BaseUnionType, Union


class MonoVariantType(BaseUnionType):

    def __init__(self, location, fields):
        BaseUnionType.__init__(self, location, fields)
        self.llvm_type = ir.LiteralStructType([
            self.get_largest_field(),
            ir.IntType(utils.round_up_to_multiple(len(self.fields), 8))
        ])

    @cached_property
    def mname(self):
        return ''.join([
            '7variant', ''.join(f.type.mname for f in self.fields)
        ])


class VariantType(SylvaParamType):

    def get_or_create_monomorphization(self, location, fields):
        for mm in self.monomorphizations:
            if (len(fields) == len(mm.fields) and all(
                    f.type == mmf.type for f, mmf in zip(fields, mm.fields))):
                return mm

        mm = MonoVariantType(location, fields)

        self.add_monomorphization(mm)

        return mm


class Variant(Union):
    pass

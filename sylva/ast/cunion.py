from functools import cached_property

from llvmlite import ir

from ..location import Location
from .sylva_type import SylvaParamType
from .union import BaseUnionType, Union


class MonoCUnionType(BaseUnionType):

    def __init__(self, location, fields):
        BaseUnionType.__init__(self, location, fields)
        self.llvm_type = ir.LiteralStructType([self.get_largest_field()])

    @cached_property
    def mname(self):
        return ''.join(['6cunion', ''.join(f.type.mname for f in self.fields)])


class CUnionType(SylvaParamType):

    def get_or_create_monomorphization(self, fields):
        for mm in self.monomorphizations:
            if (len(fields) == len(mm.fields) and all(
                    f.type == mmf.type for f, mmf in zip(fields, mm.fields))):
                return mm

        mm = MonoCUnionType(Location.Generate(), fields)

        self.add_monomorphization(mm)

        return mm


class CUnion(Union):
    pass

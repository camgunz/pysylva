from functools import cached_property

from llvmlite import ir

# from .sylva_type import SylvaParamType
from .union import BaseUnionType, Union


class CUnionType(BaseUnionType):

    def __init__(self, location, fields):
        BaseUnionType.__init__(self, location, fields)
        self.llvm_type = ir.LiteralStructType([self.get_largest_field()])

    @cached_property
    def mname(self):
        return ''.join(['6cunion', ''.join(f.type.mname for f in self.fields)])


# class CUnionType(SylvaParamType):
#
#     def get_or_create_monomorphization(self, location, fields):
#         for mm in self.monomorphizations:
#             if (len(fields) == len(mm.fields) and all(
#                     f.type == mf.type for f, mf in zip(fields, mm.fields))):
#                 return mm
#
#         mm = MonoCUnionType(location, fields)
#
#         self.add_monomorphization(mm)
#
#         return mm


class CUnion(Union):
    pass

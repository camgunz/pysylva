from functools import cached_property

from .defs import TypeDef
# from .sylva_type import SylvaParamType
from .union import BaseUnionType, Union


class CUnionType(BaseUnionType):

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


class CUnionTypeDef(TypeDef):

    def __init__(self, type):
        TypeDef.__init__(self, type.location, type.name, type)

    @cached_property
    def mname(self):
        return self.name


class CUnion(Union):
    pass

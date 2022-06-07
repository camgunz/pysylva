from functools import cached_property

from .. import utils
from .array import ArrayType, MonoArrayType
from .sylva_type import SylvaParamType


class MonoCArrayType(MonoArrayType):

    @cached_property
    def mname(self):
        return ''.join([
            '2ca',
            self.element_type.mname,
            utils.len_prefix(str(self.element_count))
        ])


class CArrayType(ArrayType):

    def add_monomorphization(self, location, element_type, element_count):
        return SylvaParamType.add_monomorphization(
            self, MonoCArrayType(location, element_type, element_count)
        )

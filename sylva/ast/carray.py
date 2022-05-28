from functools import cached_property

from .. import utils
from ..location import Location
from .array import ArrayType, MonoArrayType


class MonoCArrayType(MonoArrayType):

    @cached_property
    def mname(self):
        return ''.join([
            '2ca',
            self.element_type.mname,
            utils.len_prefix(str(self.element_count))
        ])


class CArrayType(ArrayType):

    def get_or_create_monomorphization(self, element_type, element_count):
        for mm in self.monomorphizations:
            if mm.element_type != element_type:
                continue
            if mm.element_count != element_count:
                continue
            return mm
        mm = MonoCArrayType(
            Location.Generate(),
            element_type=element_type,
            element_count=element_count
        )

        self.add_monomorphization(mm)

        return mm

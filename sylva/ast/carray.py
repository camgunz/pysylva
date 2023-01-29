from dataclasses import dataclass, field
from functools import cached_property

from .. import utils
from .array import ArrayType, MonoArrayType


@dataclass(kw_only=True)
class MonoCArrayType(MonoArrayType):

    @cached_property
    def mname(self):
        return ''.join([
            '2ca',
            self.element_type.mname,
            utils.len_prefix(str(self.element_count))
        ])


@dataclass(kw_only=True)
class CArrayType(ArrayType):
    name: str = field(init=False, default='carray')

    # pylint: disable=arguments-differ
    def get_or_create_monomorphization(
        self, location, element_type, element_count
    ):
        for n, mm in enumerate(self.monomorphizations):
            if mm.equals_params(element_type, element_count):
                return n, mm

        index = len(self.monomorphizations)

        mm = MonoCArrayType(
            location=location,
            element_type=element_type,
            element_count=element_count
        )
        self.monomorphizations.append(mm)

        return index, mm

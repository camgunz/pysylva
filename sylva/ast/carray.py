from functools import cached_property

from attrs import define, field

from .. import utils
from .array import MonoArrayType


@define(eq=False, slots=True)
class CArrayType(MonoArrayType):
    # [TODO] I think these... are also now Param?
    element_count = field()

    @cached_property
    def mname(self):
        return ''.join([
            '2ca',
            self.element_type.mname,
            utils.len_prefix(str(self.element_count))
        ])

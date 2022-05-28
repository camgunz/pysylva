from functools import cached_property

from .. import errors
from .sylva_type import SylvaType


class RangeType(SylvaType):

    def __init__(self, location, min, max):
        if min.type != max.type:
            raise errors.MismatchedRangeTypes(location, min.type, max.type)
        SylvaType.__init__(self, location)
        self.type = min.type
        self.min = min
        self.max = max
        self.llvm_type = self.type.llvm_type

    @cached_property
    def mname(self):
        return self.type.mname

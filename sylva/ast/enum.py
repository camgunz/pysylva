from functools import cached_property

from .. import errors, utils
from .sylva_type import SylvaType


class EnumType(SylvaType):

    def __init__(self, location, values):
        SylvaType.__init__(self, location)
        if len(values) <= 0:
            raise errors.EmptyEnum(self.location)

        dupes = utils.get_dupes(v.name for v in values)
        if dupes:
            raise errors.DuplicateFields(self, dupes)

        first_type = values[0].type
        for value in values[1:]:
            if value.type != first_type:
                raise errors.MismatchedEnumMemberType(first_type, value)

        self.values = values
        self.llvm_type = self.values[0].type.llvm_type

    def get_attribute(self, name):
        for val in self.values:
            if val.name == name:
                return val

    @cached_property
    def mname(self):
        return ''.join(['1e', self.values[0].type.mname])

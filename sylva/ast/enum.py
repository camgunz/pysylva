from functools import cached_property

from attrs import define, field

from .. import errors, utils
from .sylva_type import SylvaType


@define(eq=False, slots=True)
class EnumType(SylvaType):
    values = field()

    @values.validator
    def check_values(self, attribute, values):
        if len(values) <= 0:
            raise errors.EmptyEnum(self.location)

        dupes = utils.get_dupes(v.name for v in values)
        if dupes:
            raise errors.DuplicateFields(self, dupes)

        first_type = values[0].type
        for value in values[1:]:
            if value.type != first_type:
                raise errors.MismatchedEnumMemberType(first_type, value)

    @llvm_type.default # noqa: F821
    def _llvm_type_factory(self):
        return self.values[0].type.llvm_type

    def get_attribute(self, location, name):
        for val in self.values:
            if val.name == name:
                return val

    @cached_property
    def mname(self):
        return ''.join(['1e', self.values[0].type.mname])

import typing

from attrs import define, field

from .. import errors, utils
from .sylva_type import SylvaType
from .type_mapping import Field


@define(eq=False, slots=True)
class BaseUnionType(SylvaType):
    name: str | None
    implementations: typing.List = []
    fields: typing.List[Field] = field(default=[])

    # pylint: disable=unused-argument
    @fields.validator
    def check_fields(self, attribute, fields):
        dupes = utils.get_dupes(f.name for f in fields)
        if dupes:
            raise errors.DuplicateFields(self, dupes)

    def get_largest_field(self):
        largest_field = self.fields[0]
        for f in self.fields[1:]:
            if f.get_size() > largest_field.get_size():
                largest_field = f
        return largest_field.llvm_type

    # pylint: disable=unused-argument
    def get_attribute(self, location, name):
        for f in self.fields:
            if f.name == name:
                return f

import typing

from attrs import define, field

from .. import errors, utils
from .self_referential import SelfReferentialMixIn
from .sylva_type import LLVMTypeMixIn, SylvaType
from .type_mapping import Field


@define(eq=False, slots=True)
class BaseUnionType(SylvaType, LLVMTypeMixIn, SelfReferentialMixIn):
    name: str | None
    implementations: typing.List = []
    fields: typing.List[Field] = field(default=[])

    # pylint: disable=unused-argument
    @fields.validator
    def check_fields(self, attribute, fields):
        dupes = utils.get_dupes(f.name for f in fields)
        if dupes:
            raise errors.DuplicateFields(self, dupes)

    def get_largest_field(self, module):
        largest_field = self.fields[0]
        for f in self.fields[1:]:
            if f.get_size(module) > largest_field.get_size(module):
                largest_field = f
        return largest_field.get_llvm_type(module)

    # pylint: disable=unused-argument
    def get_attribute(self, location, name):
        for f in self.fields:
            if f.name == name:
                return f

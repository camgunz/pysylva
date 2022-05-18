import typing

from attrs import define, field

from .. import errors, utils
from .expr import Expr
from .sylva_type import SylvaType


@define(eq=False, slots=True)
class EnumType(SylvaType):
    values: typing.List[Expr] = field()
    implementations: typing.List = []

    # pylint: disable=unused-argument
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

    @llvm_type.default
    def _llvm_type_factory(self):
        # pylint: disable=unsubscriptable-object
        return self.values[0].type.llvm_type

    def get_attribute(self, location, name):
        for val in self.values: # pylint: disable=not-an-iterable
            if val.name == name:
                return val

from attrs import define, field

from .. import errors
from .base import Decl
from .sylva_type import SylvaType


@define(eq=False, slots=True)
class AliasDecl(Decl):
    value: str | SylvaType = field()

    # pylint: disable=unused-argument
    @value.validator
    def check_value(self, attribute, value):
        if isinstance(value, str) and value == self.name:
            raise errors.RedundantAlias(self.location, self.name)

from attrs import define

from .. import errors
from .defs import Def
from .sylva_type import SylvaType


@define(eq=False, slots=True)
class AliasDef(Def):
    value: str | SylvaType = field()

    # pylint: disable=unused-argument
    @value.validator
    def check_value(self, attribute, value):
        if isinstance(value, str) and value == self.name:
            raise errors.RedundantAlias(self.location, self.name)

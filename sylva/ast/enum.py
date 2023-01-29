from dataclasses import dataclass
from functools import cached_property

from sylva import errors, utils
from sylva.ast.expr import LiteralExpr
from sylva.ast.sylva_type import SylvaType


@dataclass(kw_only=True)
class EnumType(SylvaType):
    values: dict[str, LiteralExpr]

    def __post_init__(self):
        if len(self.values) <= 0:
            raise errors.EmptyEnum(self.location)

        dupes = utils.get_dupes(self.values.keys())
        if dupes:
            raise errors.DuplicateFields(self, dupes)

        if any(v.type != self.type for v in list(self.values.values())[1:]):
            raise errors.InconsistentEnumMemberTypes(self)

    def get_attribute(self, name):
        return self.values.get(name)

    @cached_property
    def mname(self):
        return ''.join(['1e', self.values[0].type.mname])

    @cached_property
    def type(self):
        return next(self.values.items()).type

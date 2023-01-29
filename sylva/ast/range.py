from dataclasses import dataclass
from functools import cached_property

from sylva import errors
from sylva.ast.expr import LiteralExpr
from sylva.ast.sylva_type import MonoType


@dataclass(kw_only=True)
class RangeType(MonoType):
    min: LiteralExpr
    max: LiteralExpr

    def __post_init__(self):
        if self.min.type != self.max.type:
            raise errors.MismatchedRangeTypes(
                self.location, self.min.type, self.max.type
            )
        self.type = min.type

    @cached_property
    def mname(self):
        return self.type.mname

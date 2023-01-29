from dataclasses import dataclass, field
from functools import cached_property

from sylva.ast.expr import LiteralExpr
from sylva.ast.sylva_type import SylvaType


@dataclass(kw_only=True)
class BoolType(SylvaType):
    name: str = field(init=False, default='bool')

    @cached_property
    def mname(self):
        return 'bool'


@dataclass(kw_only=True)
class BoolLiteralExpr(LiteralExpr):
    type: BoolType = field(init=False)

    def __post_init__(self):
        from .type_singleton import TypeSingletons

        self.type = TypeSingletons.BOOL

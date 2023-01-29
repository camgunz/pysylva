from dataclasses import dataclass, field
from functools import cached_property

from sylva.ast.expr import LiteralExpr
from sylva.ast.sylva_type import SylvaType


@dataclass(kw_only=True)
class RuneType(SylvaType):
    name: str = field(init=False, default='rune')

    @cached_property
    def mname(self):
        return 'rune'


@dataclass(kw_only=True)
class RuneLiteralExpr(LiteralExpr):
    type: RuneType = field(init=False)

    def __post_init__(self):
        from .type_singleton import TypeSingletons

        self.type = TypeSingletons.RUNE

from dataclasses import dataclass, field
from functools import cached_property

from sylva.ast.expr import LiteralExpr
from sylva.ast.sylva_type import MonoType


@dataclass(kw_only=True)
class CStrType(MonoType):
    name: str = field(init=False, default='cstr')

    @cached_property
    def mname(self):
        return 'cstr'


@dataclass(kw_only=True)
class CStrLiteralExpr(LiteralExpr):

    def __init__(self, location, value):
        from .type_singleton import TypeSingletons

        LiteralExpr.__init__(
            self, location=location, type=TypeSingletons.CSTR, value=value
        )

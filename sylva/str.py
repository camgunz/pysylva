from dataclasses import dataclass, field
from functools import cached_property

from sylva import utils
from sylva.array import ArrayType, MonoArrayType
from sylva.expr import LiteralExpr


@dataclass(kw_only=True)
class StrLiteralExpr(LiteralExpr):

    def __init__(self, location, value):
        from .type_singleton import TypeSingletons

        value = value.encode('utf8')

        LiteralExpr.__init__(
            self,
            location=location,
            type=TypeSingletons.STR.get_or_create_monomorphization(
                location, len(value)
            )[1],
            value=value
        )

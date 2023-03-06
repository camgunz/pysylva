from dataclasses import dataclass
from functools import cache, cached_property
from typing import Optional, Union

from sylva import errors, utils
from sylva.expr import LiteralExpr
from sylva.location import Location
from sylva.sylva_type import SylvaType


class ArrayLiteralExpr(ConstTypeLiteralExpr):
    element_type_expr: ConstExpr
    element_count_expr: ConstExpr

    def eval(self, module):
        return ARRAY.build_type(
            location=self.location,
            element_type=self.element_type_expr.eval(module),
            element_count=self.element_count_expr.eval(module),
        )

    def __init__(self, location, value):
        # [NOTE] We might know the type already because of the syntax:
        #       [int * 3][1i, 2i, 3i]
        from .type_singleton import TypeSingletons

        if len(value) == 0:
            raise errors.EmptyArray(location)

        if any(e.type != value[0].type for e in value[1:]):
            raise errors.InconsistentElementType(location, value[0].type)

        LiteralExpr.__init__(
            self,
            location=location,
            type=TypeSingletons.ARRAY.get_or_create_monomorphization(
                location, value[0].type, len(value)
            )[1],
            value=value
        )

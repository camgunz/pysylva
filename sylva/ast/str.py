from dataclasses import dataclass, field
from functools import cached_property

from sylva import utils
from sylva.ast.array import ArrayType, MonoArrayType
from sylva.ast.expr import LiteralExpr


@dataclass(kw_only=True)
class MonoStrType(MonoArrayType):

    def __init__(self, location, element_count):
        from .type_singleton import TypeSingletons

        MonoArrayType.__init__(
            self,
            location=location,
            element_type=TypeSingletons.U8,
            element_count=element_count
        )

    @cached_property
    def mname(self):
        return utils.mangle(['str', self.element_count])


@dataclass(kw_only=True)
class StrType(ArrayType):
    name: str = field(init=False, default='str')

    def __init__(self, *args, **kwargs):
        from .type_singleton import TypeSingletons

        ArrayType.__init__(
            self, element_type=TypeSingletons.U8, *args, **kwargs
        )

    # pylint: disable=arguments-differ
    def get_or_create_monomorphization(self, location, element_count):
        from .type_singleton import TypeSingletons

        for n, mm in enumerate(self.monomorphizations):
            if mm.equals_params(TypeSingletons.U8, element_count):
                return n, mm

        index = len(self.monomorphizations)

        mm = MonoStrType(location=location, element_count=element_count)
        self.monomorphizations.append(mm)

        return index, mm


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

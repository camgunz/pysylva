from functools import cached_property

from ..location import Location
from .expr import BaseExpr
from .pointer import MonoPointerType, PointerType


class MonoCPtrType(MonoPointerType):

    def __init__(self, location, referenced_type):
        MonoPointerType.__init__(
            self,
            location,
            referenced_type,
            is_reference=False,
            is_exclusive=False
        )

    @cached_property
    def mname(self):
        return ''.join(['2cp', self.referenced_type.mname])


class CPtrType(PointerType):

    # pylint: disable=arguments-differ
    def get_or_create_monomorphization(self, referenced_type):
        for mm in self.monomorphizations:
            if mm.referenced_type == referenced_type:
                return mm

        mm = MonoCPtrType(Location.Generate(), referenced_type)

        self.add_monomorphization(mm)

        return mm


class CPtrExpr(BaseExpr):

    def __init__(self, location, expr):
        from .type_singleton import TypeSingletons

        BaseExpr.__init__(
            self,
            location,
            TypeSingletons.CPTR.value.get_or_create_monomorphization(
                expr.type
            )
        )
        self.expr = expr

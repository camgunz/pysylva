from functools import cached_property

from .expr import BaseExpr
from .pointer import MonoPointerType, PointerType


class MonoCPtrType(MonoPointerType):

    def __init__(
        self,
        location,
        referenced_type,
        is_exclusive,
        referenced_type_is_exclusive
    ):
        MonoPointerType.__init__(
            self,
            location,
            referenced_type,
            is_reference=False,
            is_exclusive=is_exclusive
        )
        self.referenced_type_is_exclusive = referenced_type_is_exclusive

    @cached_property
    def mname(self):
        ex = 'x' if self.is_exclusive else 's'
        ref_ex = 'x' if self.referenced_type_is_exclusive else 's'
        return ''.join([f'4cp{ex}{ref_ex}', self.referenced_type.mname])


class CPtrType(PointerType):

    # pylint: disable=arguments-differ,arguments-renamed
    def get_or_create_monomorphization(
        self,
        location,
        referenced_type,
        is_exclusive,
        referenced_type_is_exclusive
    ):
        for mm in self.monomorphizations:
            if mm.referenced_type != referenced_type:
                continue
            if mm.is_exclusive != is_exclusive:
                continue
            if mm.referenced_type_is_exclusive:
                continue
            return mm

        mm = MonoCPtrType(
            location,
            referenced_type,
            is_exclusive,
            referenced_type_is_exclusive
        )

        self.add_monomorphization(mm)

        return mm


class CPtrExpr(BaseExpr):

    def __init__(
        self, location, expr, is_exclusive, referenced_type_is_exclusive
    ):
        from .type_singleton import TypeSingletons

        BaseExpr.__init__(
            self,
            location,
            TypeSingletons.CPTR.get_or_create_monomorphization(
                location,
                expr.type,
                is_exclusive,
                referenced_type_is_exclusive
            )
        )
        self.expr = expr

from functools import cached_property

from .expr import BaseExpr
from .pointer import MonoPointerType
from .sylva_type import SylvaParamType, SylvaType


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

    def __eq__(self, other):
        return SylvaType.__eq__(self, other) and self.equals_params(
            other.referenced_type,
            other.is_exclusive,
            other.referenced_type_is_exclusive
        )

    # pylint: disable=arguments-differ,arguments-renamed
    def equals_params(
        self, referenced_type, is_exclusive, referenced_type_is_exclusive
    ):
        return (
            self.referenced_type == referenced_type and
            self.is_exclusive == is_exclusive and
            self.referenced_type_is_exclusive == referenced_type_is_exclusive
        )


class CPtrType(SylvaParamType):

    # pylint: disable=arguments-differ,arguments-renamed
    def get_or_create_monomorphization(
        self,
        location,
        referenced_type,
        is_exclusive,
        referenced_type_is_exclusive
    ):
        for n, mm in enumerate(self.monomorphizations):
            if mm.equals_params(referenced_type,
                                is_exclusive,
                                referenced_type_is_exclusive):
                return n, mm

        index = len(self.monomorphizations)

        mm = MonoCPtrType(
            location,
            referenced_type,
            is_exclusive,
            referenced_type_is_exclusive
        )
        self.monomorphizations.append(mm)

        return index, mm


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
            )[1]
        )
        self.expr = expr

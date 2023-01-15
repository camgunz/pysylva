from functools import cached_property

from .expr import BaseExpr
from .sylva_type import SylvaParamType, SylvaType


class MonoPointerType(SylvaType):

    def __init__(self, location, referenced_type, is_reference, is_exclusive):
        SylvaType.__init__(self, location)
        self.referenced_type = referenced_type
        self.is_reference = is_reference
        self.is_exclusive = is_exclusive

    # def get_attribute(self, name):
    #     return self.referenced_type.get_attribute(name)

    # def get_reflection_attribute(self, name):
    #     return self.referenced_type.get_reflection_attribute(name)

    @cached_property
    def mname(self):
        if not self.is_reference:
            pointer_type = 'o'
        elif self.is_exclusive:
            pointer_type = 'x'
        else:
            pointer_type = 'r'
        return ''.join([f'2p{pointer_type}', self.referenced_type.mname])

    def __eq__(self, other):
        return SylvaType.__eq__(self, other) and self.equals_params(
            other.referenced_type, other.is_reference, other.is_exclusive
        )

    # pylint: disable=arguments-differ
    def equals_params(self, referenced_type, is_reference, is_exclusive):
        return (
            self.referenced_type == referenced_type and
            self.is_reference == is_reference and
            self.is_exclusive == is_exclusive
        )


class PointerType(SylvaParamType):

    # pylint: disable=arguments-differ
    def get_or_create_monomorphization(
        self, location, referenced_type, is_reference, is_exclusive
    ):
        for n, mm in enumerate(self.monomorphizations):
            if mm.equals_params(referenced_type, is_reference, is_exclusive):
                return n, mm

        index = len(self.monomorphizations)

        mm = MonoPointerType(
            location=location,
            referenced_type=referenced_type,
            is_reference=is_reference,
            is_exclusive=is_exclusive
        )
        self.monomorphizations.append(mm)

        return index, mm


class PointerExpr(BaseExpr):

    def __init__(self, location, expr, is_reference, is_exclusive):
        from .type_singleton import TypeSingletons

        pointer_type = TypeSingletons.POINTER.get_or_create_monomorphization(
            location=location,
            referenced_type=expr.type,
            is_reference=is_reference,
            is_exclusive=is_exclusive
        )[1]

        BaseExpr.__init__(self, location, pointer_type)

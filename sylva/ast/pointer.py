from functools import cached_property

from llvmlite import ir

from .expr import BaseExpr
from .sylva_type import SylvaParamType, SylvaType


class MonoPointerType(SylvaType):

    def __init__(self, location, referenced_type, is_reference, is_exclusive):
        SylvaType.__init__(self, location)
        self.llvm_type = ir.PointerType(referenced_type.llvm_type)
        self.referenced_type = referenced_type
        self.is_reference = is_reference
        self.is_exclusive = is_exclusive

    def __eq__(self, other):
        return all(
            SylvaType.__eq__(self, other) and
            self.referenced_type == other.referenced_type and
            self.is_reference == other.is_reference and
            self.is_exclusive == other.is_exclusive
        )

    def get_attribute(self, name):
        return self.referenced_type.get_attribute(name)

    @cached_property
    def mname(self):
        if not self.is_reference:
            pointer_type = 'o'
        elif self.is_exclusive:
            pointer_type = 'x'
        else:
            pointer_type = 'r'
        return ''.join([f'2p{pointer_type}', self.referenced_type.mname])


class PointerType(SylvaParamType):

    def get_or_create_monomorphization(
        self, location, referenced_type, is_reference, is_exclusive
    ):
        for mm in self.monomorphizations:
            if mm.referenced_type != referenced_type:
                continue
            if mm.is_reference != is_reference:
                continue
            if mm.is_exclusive != is_exclusive:
                continue
            return mm

        mm = MonoPointerType(
            location=location,
            referenced_type=referenced_type,
            is_reference=is_reference,
            is_exclusive=is_exclusive
        )

        self.add_monomorphization(mm)

        return mm


class PointerExpr(BaseExpr):

    def __init__(self, location, expr, is_reference, is_exclusive):
        from .type_singleton import TypeSingletons

        pointer_type = TypeSingletons.POINTER.get_or_create_monomorphization(
            location=location,
            referenced_type=expr.type,
            is_reference=is_reference,
            is_exclusive=is_exclusive
        )

        BaseExpr.__init__(self, location, pointer_type)

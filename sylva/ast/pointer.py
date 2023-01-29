from dataclasses import dataclass, field
from functools import cached_property

from sylva.ast.expr import Expr
from sylva.ast.sylva_type import MonoType, ParamType, SylvaType


@dataclass(kw_only=True)
class MonoPointerType(MonoType):
    referenced_type: SylvaType
    is_reference: bool
    is_exclusive: bool

    @cached_property
    def mname(self):
        if not self.is_reference:
            pointer_type = 'o'
        elif self.is_exclusive:
            pointer_type = 'x'
        else:
            pointer_type = 'r'
        return ''.join([f'2p{pointer_type}', self.referenced_type.mname])


@dataclass(kw_only=True)
class PointerType(ParamType):
    name: str = field(init=False, default='pointer')

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


@dataclass(kw_only=True)
class PointerExpr(Expr):
    expr: Expr
    is_reference: bool
    is_exclusive: bool

    def __init__(self, location, expr, is_reference, is_exclusive):
        from .type_singleton import TypeSingletons

        Expr.__init__(
            self,
            location=location,
            type=TypeSingletons.POINTER.get_or_create_monomorphization(
                location=location,
                referenced_type=expr.type,
                is_reference=is_reference,
                is_exclusive=is_exclusive
            )[1]
        )

        self.expr = expr
        self.is_reference = is_reference
        self.is_exclusive = is_exclusive

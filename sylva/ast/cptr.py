from dataclasses import dataclass, field
from functools import cached_property

from .expr import Expr
from .pointer import MonoPointerType
from .sylva_type import ParamType


@dataclass(kw_only=True)
class MonoCPtrType(MonoPointerType):
    is_reference: bool = field(init=False, default=False)
    referenced_type_is_exclusive: bool

    @cached_property
    def mname(self):
        ex = 'x' if self.is_exclusive else 's'
        ref_ex = 'x' if self.referenced_type_is_exclusive else 's'
        return ''.join([f'4cp{ex}{ref_ex}', self.referenced_type.mname])


@dataclass(kw_only=True)
class CPtrType(ParamType):
    name: str = field(init=False, default='cptr')

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
            location=location,
            referenced_type=referenced_type,
            is_exclusive=is_exclusive,
            referenced_type_is_exclusive=referenced_type_is_exclusive
        )
        self.monomorphizations.append(mm)

        return index, mm


@dataclass(kw_only=True)
class CPtrExpr(Expr):
    expr: Expr
    is_reference: bool
    is_exclusive: bool

    def __init__(
        self, location, expr, is_exclusive, referenced_type_is_exclusive
    ):
        from .type_singleton import TypeSingletons

        Expr.__init__(
            self,
            location=location,
            type=TypeSingletons.CPTR.get_or_create_monomorphization(
                location,
                expr.type,
                is_exclusive,
                referenced_type_is_exclusive
            )[1]
        )
        self.expr = expr
        self.is_exclusive = is_exclusive
        self.referenced_type_is_exclusive = referenced_type_is_exclusive

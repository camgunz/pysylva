from dataclasses import dataclass, field
from functools import cached_property

from sylva.ast.expr import LiteralExpr
from sylva.ast.sylva_type import MonoType, ParamType, SylvaType


@dataclass(kw_only=True)
class MonoDynarrayType(MonoType):
    element_type: SylvaType

    # [NOTE] This isn't a struct with pre-defined fields because Sylva (mostly)
    #        can't represent raw pointers.

    @cached_property
    def mname(self):
        return ''.join(['2da', self.element_type.mname])


@dataclass(kw_only=True)
class DynarrayType(ParamType):
    name: str = field(init=False, default='dynarray')

    # pylint: disable=arguments-differ
    def get_or_create_monomorphization(self, location, element_type):
        for n, mm in enumerate(self.monomorphizations):
            if mm.equals_params(element_type):
                return n, mm

        index = len(self.monomorphizations)

        mm = MonoDynarrayType(location=location, element_type=element_type)
        self.monomorphizations.append(mm)

        return index, mm


@dataclass(kw_only=True)
class DynarrayLiteralExpr(LiteralExpr): # [FIXME] This involves heap allocation
    pass

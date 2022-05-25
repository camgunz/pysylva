from functools import cached_property

from attrs import define, field

from .pointer import BasePointerExpr, BasePointerType


@define(eq=False, slots=True)
class CPtrType(BasePointerType):
    referenced_type_is_exclusive = field()

    @cached_property
    def mname(self):
        return ''.join([
            '2cp',
            self.referenced_type.mname,
        ])


@define(eq=False, slots=True)
class CPtrExpr(BasePointerExpr):
    expr = field()

import typing

from attrs import define

from .expr import Expr
from .pointer import BasePointerExpr, BasePointerType


@define(eq=False, slots=True)
class CPointerType(BasePointerType):
    referenced_type_is_exclusive: bool
    implementations: typing.List = []

    @cached_property
    def mname(self):
        return ''.join([
            '2cp',
            self.referenced_type.mname,
        ])


@define(eq=False, slots=True)
class CPointerExpr(BasePointerExpr):
    type: CPointerType
    expr: Expr

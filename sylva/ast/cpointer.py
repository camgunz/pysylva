import typing

from attrs import define

from .expr import Expr
from .pointer import BasePointerExpr, BasePointerType


@define(eq=False, slots=True)
class CPointerType(BasePointerType):
    referenced_type_is_exclusive: bool
    implementations: typing.List = []


@define(eq=False, slots=True)
class CPointerCastExpr(BasePointerExpr):

    """
    "Cast" is a misnomer here because while this casts other pointer
    types, it takes a (c) pointer to non-pointer types.
    """

    type: CPointerType
    expr: Expr

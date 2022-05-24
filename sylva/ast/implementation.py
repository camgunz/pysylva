import typing

from attrs import define

from .base import Node
from .function import FunctionDef
from .interface import InterfaceType
from .sylva_type import SylvaType


@define(eq=False, slots=True)
class Implementation(Node):
    interface: InterfaceType
    implementing_type: SylvaType
    funcs: typing.List[FunctionDef]

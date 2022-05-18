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

    @classmethod
    def Def(cls, location, interface, implementing_type, funcs):
        impl = cls(
            location=location,
            interface=interface,
            implementing_type=implementing_type,
            funcs=funcs
        )
        interface.add_implementation(impl)
        implementing_type.add_implementation(impl)
        return impl

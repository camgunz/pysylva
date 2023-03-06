from dataclasses import dataclass

from sylva.fn import Fn
from sylva.iface import IfaceType
from sylva.node import Node
from sylva.sylva_type import SylvaType


@dataclass(kw_only=True)
class Impl(Node):
    interface: IfaceType
    implementing_type: SylvaType
    funcs: list[Fn]

    def __post_init__(self, location, interface, implementing_type, funcs):
        # [TODO] Ensure implementation implements all required functions
        pass

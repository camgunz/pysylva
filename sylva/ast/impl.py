from dataclasses import dataclass

from sylva.ast.fn import Fn
from sylva.ast.iface import IfaceType
from sylva.ast.node import Node
from sylva.ast.sylva_type import SylvaType


@dataclass(kw_only=True)
class Impl(Node):
    interface: IfaceType
    implementing_type: SylvaType
    funcs: list[Fn]

    def __post_init__(self, location, interface, implementing_type, funcs):
        # [TODO] Ensure implementation implements all required functions
        pass

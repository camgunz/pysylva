from dataclasses import dataclass

from sylva.ast.node import Node


@dataclass(kw_only=True)
class ModDecl(Node):
    name: str


@dataclass(kw_only=True)
class Mod(Node):
    name: str
    defs: list[Node]

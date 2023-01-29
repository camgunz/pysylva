from dataclasses import dataclass

from sylva.ast.node import Node
from sylva.ast.sylva_type import SylvaType


@dataclass(kw_only=True)
class Parameter(Node):
    type: SylvaType

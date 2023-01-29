from dataclasses import dataclass
from typing import Any

from sylva.ast.node import Node
from sylva.ast.sylva_type import SylvaType


@dataclass(kw_only=True)
class Value(Node):
    type: SylvaType
    value: Any

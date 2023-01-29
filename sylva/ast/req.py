from dataclasses import dataclass
from typing import Optional

from sylva.ast.node import Node


@dataclass(kw_only=True)
class Req(Node):
    name: str
    bound_name: Optional[str]

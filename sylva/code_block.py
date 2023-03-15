from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from sylva.expr import Expr
    from sylva.stmt import Stmt


@dataclass
class CodeBlock:
    code: list[Union['Expr', 'Stmt']] = field(default_factory=list)

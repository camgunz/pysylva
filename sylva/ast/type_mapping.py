from attrs import define

from . import ast
from .sylva_types import SylvaType


@define(eq=False, slots=True)
class BaseTypeMapping(ast.ASTNode):
    name: str
    type: SylvaType
    index: int | None = None

    @property
    def handle(self):
        return self.index if self.index is not None else self.name


@define(eq=False, slots=True)
class Parameter(BaseTypeMapping):
    pass


@define(eq=False, slots=True)
class Attribute(BaseTypeMapping):
    pass


@define(eq=False, slots=True)
class Field(BaseTypeMapping):
    pass

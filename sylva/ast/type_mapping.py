from attrs import define

from .base import Node
from .sylva_type import SylvaType


@define(eq=False, slots=True)
class BaseTypeMapping(Node):
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

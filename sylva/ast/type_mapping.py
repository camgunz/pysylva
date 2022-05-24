from attrs import define, field

from .base import Node


@define(eq=False, slots=True)
class BaseTypeMapping(Node):
    name = field()
    type = field()
    index = field(default=None)

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

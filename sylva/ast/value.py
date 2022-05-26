from attrs import define, field

from .base import Node


@define(eq=False, slots=True)
class Value(Node):
    ptr = field()
    name = field()
    type = field()

    def emit(self, module, builder, scope):
        return builder.load(self.ptr, self.name)

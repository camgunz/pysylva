from attrs import frozen

from sylva.ast.base import Node


class Bind(Node):
    type: SylvaType

    def __init__(self, location, name, type=None):
        Node.__init__(self, location)
        self.name = name
        self.type = type

    @property
    def is_type_parameter(self):
        return self.type is None

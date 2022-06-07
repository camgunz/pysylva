from .base import Node


class Bind(Node):

    def __init__(self, location, name, type=None):
        Node.__init__(self, location)
        self.name = name
        self.type = type

    @property
    def is_type_parameter(self):
        return self.type is None

    def emit(self, obj, module, builder, scope, name):
        raise NotImplementedError()

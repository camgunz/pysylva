from .base import Node


class Bind(Node):

    def __init__(self, location, name, type):
        Node.__init__(self, location)
        self.name = name
        self.type = type

    def emit(self, obj, module, builder, scope, name):
        raise NotImplementedError()

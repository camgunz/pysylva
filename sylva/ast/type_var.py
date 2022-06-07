from .base import Node


class TypeVar(Node):

    def __init__(self, location, name):
        Node.__init__(self, location)
        self.name = name

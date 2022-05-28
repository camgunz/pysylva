from .base import Node


class Impl(Node):

    def __init__(self, location, interface, implementing_type, funcs):
        Node.__init__(self, location)
        self.interface = interface
        self.implementing_type = implementing_type
        self.funcs = funcs

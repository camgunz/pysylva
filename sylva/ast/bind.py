from .base import Decl


class Bind(Decl):

    def __init__(self, location, name, type):
        Decl.__init__(self, location, name)
        self.type = type

    def emit(self, obj, module, builder, scope, name):
        raise NotImplementedError()

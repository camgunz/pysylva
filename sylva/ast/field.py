from .bind import Bind


class Field(Bind):

    def __init__(self, location, name, type, index):
        Bind.__init__(self, location, name, type)
        self.index = index

    def emit(self, obj, module, builder, scope, name):
        return builder.gep(obj, [self.index], inbounds=True, name=name)

from .bind import Bind


class Attribute(Bind):

    def __init__(self, location, name, type, func=None):
        Bind.__init__(self, location, name, type)
        self.func = func

    def emit(self, obj, module, builder, scope, name):
        if not self.func:
            raise Exception(f'Attribute {self.name} has no action')
        return self.func(obj, self.location, module, builder, scope)

from .bind import Bind


class Attribute(Bind):

    def __init__(self, location, name, type, func=None):
        Bind.__init__(self, location, name, type)
        self.llvm_value = None
        self.func = func

    def get_llvm_value(self, *args, **kwargs):
        if self.llvm_value:
            return self.llvm_value

        if not self.func:
            raise Exception(f'Attribute {self.name} has no action')

        kwargs['location'] = self.location

        self.llvm_value = self.func(*args, **kwargs)

        return self.llvm_value

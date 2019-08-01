from . import errors


class Module:

    def __init__(self, name):
        self.name = name
        self.vars = {}

    def __repr__(self):
        return 'Module(%r)' % (self.name)

    def __str__(self):
        return f'<Module {self.name}>'

    def lookup(self, name):
        # [NOTE] Raise your own exceptions if this is bad for you
        return self.vars.get(name)

    def define(self, name, value):
        existing_value = self.lookup(name)
        if existing_value:
            raise errors.DuplicateDefinitionError(
                value.location, existing_value.location
            )
        self.vars[name] = value

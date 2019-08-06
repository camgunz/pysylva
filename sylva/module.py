from . import errors
from .parser import Parser


class Module:

    def __init__(self, program, name, locations, dependency_names):
        self.program = program
        self.name = name
        self.vars = {}
        self.locations = locations
        self.dependency_names = dependency_names
        self.dependencies = set()
        self._parsed = False

    @classmethod
    def BuiltIn(cls, program, name):
        m = cls(program, name, [], [])
        m._parsed = True
        return m

    def __repr__(self):
        return 'Module(%r, %r, %r, %r)' % (
            self.program,
            self.name,
            self.locations,
            self.dependency_names
        )

    def __str__(self):
        return f'<Module {self.name}>'

    def resolve_dependencies(self, seen=None):
        if len(self.dependencies) == len(self.dependency_names):
            return
        seen = seen or []
        if self in seen:
            raise errors.CircularDependency(self, seen)
        seen.append(self)
        self.dependencies = set()
        for dependency_name in self.dependency_names:
            module = self.program.get_module(dependency_name)
            if not module:
                # [TODO] Use a LocationError here, which requires storing
                #        locations as well as names
                raise errors.NoSuchModule(dependency_name)
            self.dependencies.add(module)
        for dependency in self.dependencies:
            dependency.resolve_dependencies(seen)

    def parse(self):
        print(f'{self.name}: Parsing')
        # if self.name == 'jungle.plants.trees':
        #     import pdb
        #     pdb.set_trace()
        if self._parsed:
            return
        self._parsed = True
        for dependency in self.dependencies:
            print(f'{self.name}: Parsing dependency {dependency.name}')
            dependency.parse()
        for location in self.locations:
            Parser(self, location).parse()

    def lookup(self, name):
        # [NOTE] Raise your own exceptions if this is bad for you
        print(f'{self.name}: Looking up {name}')
        return self.vars.get(name)

    def define(self, name, value):
        print(f'{self.name}: Defining {name}: {value}')
        existing_value = self.lookup(name)
        if existing_value:
            raise errors.DuplicateDefinition(
                value.location, existing_value.location
            )
        self.vars[name] = value

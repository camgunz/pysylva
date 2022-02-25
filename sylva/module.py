from . import errors
from .parser import Parser


class Module:

    def __init__(self, program, name, data_sources, requirement_statements):
        self.program = program
        self.name = name
        self.vars = {}
        self.data_sources = data_sources
        self.requirement_statements = requirement_statements
        self.requirements = set()
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
            self.data_sources,
            self.requirement_statements
        )

    def __str__(self):
        return f'<Module {self.name}>'

    def resolve_requirements(self, seen=None):
        if len(self.requirements) == len(self.requirement_statements):
            return
        seen = seen or []
        if self in seen:
            raise errors.CircularDependency(self, seen)
        seen.append(self)
        self.requirements = set()
        for requirement_statement in self.requirement_statements:
            module = self.program.get_module(requirement_statement.name)
            if not module:
                raise errors.NoSuchModule(
                    requirement_statement.location,
                    requirement_statement.name
                )
            self.requirements.add(module)
        for requirement in self.requirements:
            requirement.resolve_requirements(seen)

    def parse(self):
        if self._parsed:
            return
        self._parsed = True
        for requirement in self.requirements:
            requirement.parse()
        for data_source in self.data_sources:
            Parser(self, data_source).parse()

    def lookup(self, name):
        # [NOTE] Raise your own exceptions if this is bad for you
        return self.vars.get(name)

    def define(self, name, value):
        existing_value = self.lookup(name)
        if existing_value:
            raise errors.DuplicateDefinition(
                value.location, existing_value.location
            )
        self.vars[name] = value

from . import debug, errors, types
from .codegen import CodeGen
from .module_builder import ModuleBuilder
from .module_checker import ModuleChecker
from .parser_utils import parse_with_listener


class Module: # pylint: disable=too-many-instance-attributes

    def __init__(self, program, name, streams, requirement_statements):
        self._program = program
        self._name = name
        self._streams = streams
        self._requirement_statements = requirement_statements
        self._parsed = False

        self._aliases = {}
        self.vars = {}

        self.requirements = set()

    @property
    def name(self):
        return self._name

    def __repr__(self):
        return 'Module(%r, %r, %r, %r)' % (
            self._program,
            self._name,
            self._streams,
            self._requirement_statements
        )

    def __str__(self):
        return f'<Module {self.name}>'

    def resolve_requirements(self, seen=None):
        if len(self.requirements) == len(self._requirement_statements):
            return
        seen = seen or set()
        if self in seen:
            raise errors.CircularDependency(self, seen)
        seen.add(self)
        for requirement_statement in self._requirement_statements:
            module = self._program.get_module(requirement_statement.name)
            if not module:
                raise errors.NoSuchModule(
                    requirement_statement.location, requirement_statement.name
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
        for stream in self._streams:
            module_builder = ModuleBuilder(self)
            parse_with_listener(stream, module_builder)

    def check(self):
        ModuleChecker(self).check()

    def get_ir(self):
        self.parse()
        return CodeGen(self).compile_module()

    def add_alias(self, name, value):
        debug('module_builder', f'alias {name} -> {value}')
        existing_alias = self._aliases.get(name)
        if existing_alias:
            raise errors.DuplicateAlias(
                value.location, existing_alias.location, name
            )
        self._aliases[name] = value

    def lookup(self, name):
        aliased_value = self._aliases.get(name)
        if aliased_value:
            return aliased_value
        local_value = self.vars.get(name)
        if local_value:
            return local_value
        if '.' in name:
            module, name = name.split('.', 1)
            self._program.get_module(module)
            if module:
                return module.lookup(name)
        return types.BUILTINS.get(name)

    def define(self, name, value):
        debug('module_builder', f'define {self.name}.{name} -> {value}')
        existing_value = self.vars.get(name)
        if existing_value:
            raise errors.DuplicateDefinition(
                value.location, existing_value.location
            )
        if '.' in name and self._program.get_module(name.split('.', 1)[0]):
            raise errors.DefinitionViolation(value.location, name)
        if name in types.BUILTINS:
            raise errors.RedefinedBuiltIn(value.location, name)
        self.vars[name] = value

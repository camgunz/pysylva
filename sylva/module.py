# import re
import lark

from . import ast, debug, errors
from .code_gen import CodeGen
from .location import Location
from .module_builder import ModuleBuilder

# _IDENTIFIER_DELIMITERS = re.compile(r'(\.|::)')


class Module(ast.Dotable):

    def __init__(self, program, name, streams, requirement_statements):
        self._program = program
        self._name = name
        self._streams = streams
        self._requirement_statements = requirement_statements
        self._parsed = False
        self._errors = []
        self._aliases = {}

        self._code_gen = CodeGen(self)
        self.vars = {}
        self.vars.update(ast.BUILTIN_TYPES)
        self.requirements = set()
        self.type = ast.ModuleType(Location.Generate(), self)

    @property
    def name(self):
        return self._name

    @property
    def target(self):
        return self._program.target

    def __repr__(self):
        return 'Module(%r, %r, %r, %r)' % (
            self._program,
            self._name,
            self._streams,
            self._requirement_statements
        )

    def __str__(self):
        return f'<Module {self.name}>'

    def _check_definition(self, definition):
        existing_alias = self._aliases.get(definition.name)
        if existing_alias:
            raise errors.DuplicateAlias(
                definition.location, existing_alias.location, definition.name
            )

        existing_definition = self.vars.get(definition.name)
        if existing_definition:
            raise errors.DuplicateDefinition(
                definition,
                existing_definition.location,
            )

        if definition.name in ast.BUILTIN_TYPES:
            raise errors.RedefinedBuiltIn(definition)

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
            self.vars[module.name] = module
        for requirement in self.requirements:
            requirement.resolve_requirements(seen)

    def parse(self):
        if self._parsed:
            return self._errors

        for s in self._streams:
            parser = lark.Lark.open(
                'Sylva.lark',
                rel_to=__file__,
                parser='lalr',
                propagate_positions=True,
                maybe_placeholders=True,
                start='module',
            )

            ModuleBuilder(self, s).visit(parser.parse(s.data))

        for name, obj in self.vars.items():
            if isinstance(obj, ast.SylvaType):
                self._errors.extend(obj.check())

            if isinstance(obj, ast.MetaSylvaType):
                self._errors.extend(obj.resolve_self_references(name))

        self._parsed = True

        return self._errors

    def get_llvm_module(self):
        self.parse()

        if self._errors:
            return None, self._errors

        return self._code_gen.get_llvm_module()

    def get_object_code(self):
        self.parse()

        if self._errors:
            return None, self._errors

        return self._code_gen.get_object_code()

    def get_attribute(self, location, name):
        aliased_value = self._aliases.get(name)
        if aliased_value is not None:
            return ast.Attribute(
                location=location,
                name=name,
                type=aliased_value.value,
                index=None
            )

        attribute_type = self.vars.get(name)
        if attribute_type is None:
            return None

        if not isinstance(attribute_type, ast.SylvaType):
            attribute_type = attribute_type.type

        return ast.Attribute(
            location=location, name=name, type=attribute_type, index=None
        )

    # def lookup_field(self, location, name):
    #     aliased_value = self._aliases.get(name)
    #     if aliased_value is not None:
    #         return aliased_value.value

    #     fields = _IDENTIFIER_DELIMITERS.split(name)
    #     first_name = fields.pop(0)

    #     value = self.vars.get(first_name)

    #     while value is not None and len(fields) > 0:
    #         reflection = fields.pop(0) == '::'
    #         field = fields.pop(0)

    #         if reflection:
    #             value = value.reflect(location, field)
    #         else:
    #             value = value.lookup(location, field)

    #         if not value:
    #             raise errors.NoSuchAttribute(location, field)

    #     return value

    def define(self, definition):
        self._check_definition(definition)
        if isinstance(definition, ast.Alias):
            debug('define', f'Alias {definition.name} -> {definition}')
            self._aliases[definition.name] = definition
        elif isinstance(definition, ast.Const):
            debug('define', f'Const {definition.name} -> {definition.value}')
            self.vars[definition.name] = definition
        else:
            debug('define', f'Define {definition.name} -> {definition}')
            self.vars[definition.name] = definition

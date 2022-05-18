import typing

from attrs import define, field

from .. import debug, errors
from ..code_gen import CodeGen
from ..location import Location
from ..module_builder import ModuleBuilder
from ..parser import Parser
from ..program import Program
from ..stream import Stream
from .decl import Decl
from .defs import Def
from .operator import AttributeLookupMixIn
from .requirement import RequirementDecl
from .self_referential import SelfReferentialMixIn
from .sylva_type import SylvaType
from .type_mapping import Attribute
from .alias import AliasDecl
from .const import ConstDef


@define(eq=False, slots=True)
class ModuleType(SylvaType, AttributeLookupMixIn):
    # Module, but we can't because it would be circular
    value: typing.Any
    implementations: typing.List = []

    def get_attribute(self, location, name):
        return self.value.get_attribute(location, name)

    def lookup_attribute(self, location, name, module):
        return self.value.lookup_attribute(location, name, module)


@define(eq=False, slots=True)
class ModuleDecl(Decl):
    pass


@define(eq=False, slots=True)
class Module(Def, AttributeLookupMixIn):
    program: Program
    streams: typing.List[Stream]
    requirement_statements: typing.List[RequirementDecl]
    parsed = False
    errors: typing.List[errors.LocationError] = []
    aliases: typing.Dict[str, Def] = {}
    code_gen = field(init=False)
    vars: typing.Dict[str, Def] = {}
    requirements: typing.Set = set()
    type = field(init=False)

    @code_gen.default
    def _code_gen_factory(self):
        self.code_gen = CodeGen(self)

    @type.default
    def _type_factory(self):
        self.type = ModuleType(Location.Generate(), self)

    @property
    def target(self):
        return self.program.target

    def __repr__(self):
        return 'Module(%r, %r, %r, %r)' % (
            self.program, self.name, self.streams, self.requirement_statements
        )

    def __str__(self):
        return f'<Module {self.name}>'

    def _check_definition(self, definition):
        existing_alias = self.aliases.get(definition.name)
        if existing_alias:
            raise errors.DuplicateAlias(
                definition.location, existing_alias.location, definition.name
            )

        # if definition.name in ast.BUILTIN_TYPES:
        #     raise errors.RedefinedBuiltIn(definition)

        existing_definition = self.vars.get(definition.name)
        if existing_definition:
            raise errors.DuplicateDefinition(
                definition.name,
                definition.location,
                existing_definition.location,
            )

    def resolve_requirements(self, seen=None):
        if len(self.requirements) == len(self.requirement_statements):
            return
        seen = seen or set()
        if self in seen:
            raise errors.CircularDependency(self, seen)
        seen.add(self)
        for requirement_statement in self.requirement_statements:
            module = self.program.get_module(requirement_statement.name)
            if not module:
                raise errors.NoSuchModule(
                    requirement_statement.location, requirement_statement.name
                )
            self.requirements.add(module)
            self.vars[module.name] = module
        for requirement in self.requirements:
            requirement.resolve_requirements(seen)

    def parse(self):
        if self.parsed:
            return self.errors

        for s in self.streams:
            ModuleBuilder(self, s).visit(Parser().parse(s.data))

        for _, obj in self.vars.items():
            # if name in ast.BUILTIN_TYPES:
            #     continue

            if isinstance(obj.type, SelfReferentialMixIn):
                self.errors.extend(obj.type.resolve_self_references())

        self.parsed = True

        return self.errors

    def get_llvm_module(self):
        self.parse()

        if self.errors:
            return None, self.errors

        return self.code_gen.get_llvm_module()

    def get_object_code(self):
        self.parse()

        if self.errors:
            return None, self.errors

        return self.code_gen.get_object_code()

    def get_attribute(self, location, name):
        aliased_value = self.aliases.get(name)
        if aliased_value is not None:
            return Attribute(
                location=location,
                name=name,
                type=aliased_value.value,
                index=None
            )

        attribute_type = self.vars.get(name)
        if attribute_type is None:
            return None

        if not isinstance(attribute_type, SylvaType):
            attribute_type = attribute_type.type

        return Attribute(
            location=location, name=name, type=attribute_type, index=None
        )

    def lookup_attribute(self, location, name, module):
        aliased_value = self.aliases.get(name)
        if aliased_value is not None:
            return aliased_value.value

        return self.vars.get(name)

    # def lookup_field(self, location, name):
    #     aliased_value = self.aliases.get(name)
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
        if isinstance(definition, AliasDecl):
            debug('define', f'Alias {definition.name} -> {definition}')
            self.aliases[definition.name] = definition
        elif isinstance(definition, ConstDef):
            debug('define', f'Const {definition.name} -> {definition.value}')
            self.vars[definition.name] = definition
        else:
            debug('define', f'Define {definition.name} -> {definition}')
            self.vars[definition.name] = definition

    def get_identified_type(self, name):
        return self.code_gen.get_identified_type(name)

import typing

from attrs import define, field
from llvmlite import ir # type: ignore

from .. import errors
from ..location import Location
from ..module_builder import ModuleBuilder
from ..parser import Parser
from ..program import Program
from ..stream import Stream
from .attribute_lookup import AttributeLookupMixIn
from .base import Decl
from .defs import TypeDef
from .requirement import RequirementDecl
from .sylva_type import SylvaType
from .type_mapping import Attribute


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
class ModuleDef(TypeDef, AttributeLookupMixIn):
    program: Program
    streams: typing.List[Stream]
    requirement_statements: typing.List[RequirementDecl]
    parsed = False
    errors: typing.List[errors.LocationError] = []
    aliases: typing.Dict[str, TypeDef] = {}
    vars: typing.Dict[str, TypeDef] = {}
    requirements: typing.Set = set()
    type = field(init=False)

    @type.default
    def _type_factory(self):
        return ModuleType(Location.Generate(), self)

    def __repr__(self):
        return 'Module(%r, %r, %r, %r)' % (
            self.program, self.name, self.streams, self.requirement_statements
        )

    def __str__(self):
        return f'<Module {self.name}>'

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

        self.parsed = True

        return self.errors

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

    def emit_attribute_lookup(self, location, name):
        aliased_value = self.aliases.get(name)
        if aliased_value is not None:
            return aliased_value.value

        return self.vars.get(name)

    # pylint: disable=arguments-differ
    def llvm_define(self):
        llvm_module = ir.Module(name=self.name)

        for var in self.vars.values():
            var.llvm_define(llvm_module)

        return llvm_module, []

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

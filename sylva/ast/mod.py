from llvmlite import ir

from .. import errors
from ..location import Location
from ..module_builder import ModuleBuilder
from ..parser import Parser
from .attribute_lookup import AttributeLookupMixIn
from .base import Decl
from .defs import TypeDef
from .sylva_type import SylvaType
from .type_mapping import Attribute


class ModType(SylvaType):

    def __init__(self, location, value):
        SylvaType.__init__(self, location)
        self.value = value

    def get_attribute(self, name):
        return self.value.get_attribute(name)

    def emit_attribute_lookup(self, module, builder, scope, name):
        return self.value.emit_attribute_lookup(module, builder, scope, name)


class ModDecl(Decl):
    pass


class ModDef(TypeDef, AttributeLookupMixIn):

    def __init__(self, name, program, streams, requirement_statements):
        location = Location.Generate()
        TypeDef.__init__(
            self, location, name=name, type=ModType(Location.Generate(), self)
        )
        AttributeLookupMixIn.__init__(self)

        self.program = program
        self.streams = streams
        self.requirement_statements = requirement_statements

        self.parsed = False
        self.errors = []
        self.aliases = {}
        self.vars = {}
        self.requirements = set()

    def __repr__(self):
        return 'Mod(%r, %r, %r, %r)' % (
            self.program, self.name, self.streams, self.requirement_statements
        )

    def __str__(self):
        return f'<Mod {self.name}>'

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

    def get_attribute(self, name):
        aliased_value = self.aliases.get(name)
        if aliased_value is not None:
            return Attribute(
                location=aliased_value.location,
                name=name,
                type=aliased_value.value,
            )

        attribute_type = self.vars.get(name)
        if attribute_type is None:
            return None

        if not isinstance(attribute_type, SylvaType):
            attribute_type = attribute_type.type

        return Attribute(
            location=attribute_type.location, name=name, type=attribute_type
        )

    def emit_attribute_lookup(self, module, builder, scope, name):
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

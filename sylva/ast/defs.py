import typing

from attrs import define, field
from llvmlite import ir # type: ignore

from .. import debug, errors
from ..location import Location
from .base import Node
from .pointer import BasePointerType
from .sylva_type import SylvaParamType, SylvaType
from .type_mapping import Field


@define(eq=False, slots=True)
class BaseDef(Node):
    name: str | None
    type = field()

    def _check_definition(self, module):
        existing_alias = module.aliases.get(self.name)
        if existing_alias:
            raise errors.DuplicateAlias(
                self.location, existing_alias.location, self.name
            )

        # if self.name in ast.BUILTIN_TYPES:
        #     raise errors.RedefinedBuiltIn(self)

        existing_definition = module.vars.get(self.name)
        if existing_definition:
            raise errors.DuplicateDefinition(
                self.name,
                self.location,
                existing_definition.location,
            )

    def define(self, module):
        self._check_definition(module)
        debug('define', f'Define {self.name} -> {self}')
        module.vars[self.name] = self


@define(eq=False, slots=True)
class Def(BaseDef):
    type: SylvaType


@define(eq=False, slots=True)
class ParamDef(BaseDef):
    type: SylvaParamType


@define(eq=False, slots=True)
class DeferredTypeLookup:
    location: Location
    value: str


@define(eq=False, slots=True)
class SelfReferentialMixIn:
    name: str | None
    fields: typing.List[Field] = []
    llvm_type: ir.Type | None = None

    def _resolve_self_references(self):
        missing_field_errors = []

        for f in self.fields:
            if not isinstance(f.type, BasePointerType):
                continue
            if not isinstance(f.type.referenced_type, DeferredTypeLookup):
                continue
            pointer = f.type
            deferred_lookup = pointer.referenced_type
            if self.name is not None and deferred_lookup.value == self.name:
                pointer.referenced_type = self
            else:
                missing_field_errors.append(
                    errors.UndefinedSymbol(
                        deferred_lookup.location, deferred_lookup.value
                    )
                )

        return missing_field_errors

    def define(self, module):
        self._resolve_self_references()
        # [TODO] Actually write
        if self.name is None:
            for f in self.fields:
                if not isinstance(f.type, BasePointerType):
                    continue
                if not f.type.referenced_type == self:
                    continue
                raise Exception(
                    'Self-referential literals cannot be anonymous'
                )
            struct = ir.LiteralStructType([
                f.type.llvm_type for f in self.fields
            ])
        else:
            struct = module.get_identified_type(self.name)
            fields = []
            for f in self.fields:
                if not isinstance(f.type, BasePointerType):
                    fields.append(f.type.llvm_type)
                elif not f.type.referenced_type == self:
                    fields.append(f.type.llvm_type)
                else:
                    fields.append(ir.PointerType(struct))
            struct.set_body(*fields)

        self.llvm_type = struct

        return struct


@define(eq=False, slots=True)
class SelfReferentialDef(SelfReferentialMixIn, Def):
    name: str
    fields: typing.List[Field] = []
    llvm_type: ir.Type | None = None


@define(eq=False, slots=True)
class SelfReferentialParamDef(SelfReferentialMixIn, ParamDef):
    name: str
    fields: typing.List[Field] = []
    llvm_type: ir.Type | None = None

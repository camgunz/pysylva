from functools import cached_property

from attrs import define, field
from llvmlite import ir

from .. import debug, errors
from .base import Node
from .pointer import BasePointerType


@define(eq=False, slots=True)
class BaseDef(Node):
    name = field()
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
        debug('define', f'Define {self.name} ({self.mname}) -> {self}')
        module.vars[self.mname] = self

    def llvm_define(self, llvm_module):
        return ir.GlobalVariable(llvm_module, self.type.llvm_type, self.mname)

    @cached_property
    def mname(self):
        return self.name


@define(eq=False, slots=True)
class TypeDef(BaseDef):
    pass


@define(eq=False, slots=True)
class ParamTypeDef(BaseDef):
    pass


@define(eq=False, slots=True)
class DeferredTypeLookup:
    location = field()
    value = field()


@define(eq=False, slots=True)
class SelfReferentialMixIn:

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

    def llvm_define(self, llvm_module):
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
            struct = llvm_module.context.get_identified_type(self.name)
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
class SelfReferentialTypeDef(SelfReferentialMixIn, TypeDef):

    def define(self, module):
        self._resolve_self_references()
        super().define(module)


@define(eq=False, slots=True)
class SelfReferentialParamTypeDef(SelfReferentialMixIn, ParamTypeDef):

    def define(self, module):
        self._resolve_self_references()
        super().define(module)

from functools import cached_property

from llvmlite import ir

from .. import debug, errors
from .base import Node
from .pointer import BasePointerType


class BaseDef(Node):

    def __init__(self, location, name, type):
        Node.__init__(self, location)
        self.name = name
        self.type = type

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


class TypeDef(BaseDef):
    pass


class ParamTypeDef(BaseDef):
    pass


class DeferredTypeLookup:

    def __init__(self, location, value):
        self.location = location
        self.value = value


class SelfReferentialMixIn:

    def _resolve_self_references(self):
        missing_field_errors = []

        for f in self.fields: # pylint: disable=no-member
            if not isinstance(f.type, BasePointerType):
                continue
            if not isinstance(f.type.referenced_type, DeferredTypeLookup):
                continue
            pointer = f.type
            deferred_lookup = pointer.referenced_type
            # pylint: disable=no-member
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
        # pylint: disable=no-member
        if self.name is None:
            for f in self.fields: # pylint: disable=no-member
                if not isinstance(f.type, BasePointerType):
                    continue
                if not f.type.referenced_type == self:
                    continue
                raise Exception(
                    'Self-referential literals cannot be anonymous'
                )
            # pylint: disable=no-member
            struct = ir.LiteralStructType([
                f.type.llvm_type for f in self.fields
            ])
        else:
            # pylint: disable=no-member
            struct = llvm_module.context.get_identified_type(self.name)
            fields = []
            for f in self.fields: # pylint: disable=no-member
                if not isinstance(f.type, BasePointerType):
                    fields.append(f.type.llvm_type)
                elif not f.type.referenced_type == self:
                    fields.append(f.type.llvm_type)
                else:
                    fields.append(ir.PointerType(struct))
            struct.set_body(*fields)

        # pylint: disable=attribute-defined-outside-init
        self.llvm_type = struct

        return struct


class SelfReferentialTypeDef(SelfReferentialMixIn, TypeDef):

    def define(self, module):
        self._resolve_self_references()
        super().define(module)


class SelfReferentialParamTypeDef(SelfReferentialMixIn, ParamTypeDef):

    def define(self, module):
        self._resolve_self_references()
        super().define(module)

from functools import cached_property

from llvmlite import ir

from .. import debug, errors, utils
from .bind import Bind
from .pointer import PointerType


class BaseDef(Bind):

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

    def emit(self, obj, module, builder, scope, name):
        raise NotImplementedError()


class TypeDef(BaseDef):

    def define(self, module):
        self._check_definition(module)
        debug('define', f'Define {self.name} ({self.mname}) -> {self}')
        module.vars[self.mname] = self

    @cached_property
    def mname(self):
        return ''.join([utils.len_prefix(self.name), self.type.mname])


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
            if not isinstance(f.type, PointerType):
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

    # pylint: disable=unused-argument
    def emit(self, obj, module, builder, scope, name):
        llvm_module = module.type.llvm_type
        # pylint: disable=no-member
        if self.name is None:
            for f in self.fields: # pylint: disable=no-member
                if not isinstance(f.type, PointerType):
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
                if not isinstance(f.type, PointerType):
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

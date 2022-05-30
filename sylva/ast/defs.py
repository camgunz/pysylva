from functools import cached_property

from llvmlite import ir

from .. import debug, errors
from .bind import Bind


class BaseDef(Bind):

    def _check_definition(self, module):
        existing_alias = module.aliases.get(self.name)
        if existing_alias:
            raise errors.DuplicateAlias(
                self.location, existing_alias.location, self.name
            )

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
        return self.type.mname

    def emit(self, obj, module, builder, scope, name):
        llvm_module = module.type.llvm_type
        return ir.GlobalVariable(llvm_module, self.type.llvm_type, self.name)


class ParamTypeDef(BaseDef):
    pass

from functools import cached_property

from llvmlite import ir

from .. import debug, errors
from .bind import Bind


class BaseDef(Bind):

    def __init__(self, location, name, type=None):
        Bind.__init__(self, location, name, type=type)
        self.llvm_value = None

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

    def emit(self, *args, **kwargs):
        module = kwargs['module']

        self._check_definition(module)
        debug('define', f'Define {self.name} -> {self}')
        module.vars[self.name] = self

        if self.type.llvm_type:
            llvm_value = self.get_llvm_value(*args, **kwargs)
            return llvm_value

        return self


class TypeDef(BaseDef):

    def get_llvm_value(self, *args, **kwargs):
        module = kwargs['module']
        return ir.GlobalVariable(
            module.type.llvm_type, self.type.llvm_type, self.name
        )

    @cached_property
    def mname(self):
        return self.type.mname


class ParamTypeDef(BaseDef):
    pass

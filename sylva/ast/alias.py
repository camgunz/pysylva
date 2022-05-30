from .. import debug, errors
from ..llvm_alias import Alias as LLVMAlias
from .defs import BaseDef
from .sylva_type import SylvaType


class Alias(BaseDef):

    def __init__(self, location, name, value):
        if isinstance(value, SylvaType):
            type = value
        elif value == self.name:
            raise errors.RedundantAlias(self.location, self.name)
        else:
            type = value.type

        BaseDef.__init__(self, location, name, type)

        self.value = value

    def define(self, module):
        self._check_definition(module)
        name = ( # yapf: disable
            self.value.mname
            if isinstance(self.value, SylvaType)
            else self.value
        )
        debug('define', f'Alias {self.name} ({name}) -> {self}')
        module.vars[self.name] = self

    def emit(self, obj, module, builder, scope, name):
        llvm_module = module.type.llvm_type

        if isinstance(self.value, str):
            target = llvm_module.get_global(self.value)
            type = target.type
        elif isinstance(self.value, SylvaType):
            target = self.value.llvm_type
            type = target

        return LLVMAlias(
            module=llvm_module,
            name=self.name,
            target=target,
            type=type,
            linkage='internal'
        )

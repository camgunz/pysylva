from .. import debug, errors
from ..LLVMAlias import Alias as LLVMAlias
from .defs import BaseDef
from .sylva_type import SylvaType


class AliasDef(BaseDef):

    def __init__(self, location, name, type, value):
        BaseDef.__init__(self, location, name, type)

        if isinstance(value, str) and value == self.name:
            raise errors.RedundantAlias(self.location, self.name)

        self.value = value

    def define(self, module):
        self._check_definition(module)
        name = ( # yapf: disable
            self.value.mname
            if isinstance(self.value, SylvaType)
            else self.value
        )
        debug('define', f'Alias {self.name} ({name}) -> {self}')
        module.vars[name] = self

    def llvm_define(self, llvm_module):
        if isinstance(self.value, str):
            target = llvm_module.get_global(self.value)
        elif isinstance(self.value, SylvaType):
            target = self.value.llvm_type

        return LLVMAlias(
            module=llvm_module,
            name=self.name,
            target=target,
            linkage='internal'
        )

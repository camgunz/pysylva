from attrs import frozen

from .. import debug, errors
from ..llvm_alias import Alias as LLVMAlias
from .defs import BaseDef
from .sylva_type import SylvaType


class Alias(BaseDef):

    def __init__(self, location, name, value):
        if isinstance(value, SylvaType):
            type = value
        elif value == name:
            raise errors.RedundantAlias(location, name)
        else:
            type = value.type

        BaseDef.__init__(self, location, name, type)

        self.value = value

    def emit(self, *args, **kwargs):
        module = kwargs['module']
        llvm_module = module.type.llvm_type

        if self.llvm_value:
            return self.llvm_value

        self._check_definition(module)

        name = ( # yapf: disable
            self.value.mname
            if isinstance(self.value, SylvaType)
            else self.value
        )
        debug('define', f'Alias {self.name} ({name}) -> {self}')
        module.vars[self.name] = self

        if isinstance(self.value, str):
            target = llvm_module.get_global(self.value)
            type = target.type
        elif isinstance(self.value, SylvaType):
            target = self.value.llvm_type
            type = target

        self.llvm_value = LLVMAlias(
            module=llvm_module,
            name=self.name,
            target=target,
            type=type,
            linkage='internal'
        )

        return self.llvm_value

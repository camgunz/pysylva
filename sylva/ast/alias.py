from attrs import define as attrs_define, field

from .. import debug, errors
from ..LLVMAlias import Alias
from .defs import BaseDef
from .sylva_type import SylvaType


@attrs_define(eq=False, slots=True)
class AliasDef(BaseDef):
    value: str | SylvaType = field()

    # pylint: disable=unused-argument
    @value.validator
    def check_value(self, attribute, value):
        if isinstance(value, str) and value == self.name:
            raise errors.RedundantAlias(self.location, self.name)

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

        return Alias(
            module=llvm_module,
            name=self.name,
            target=target,
            linkage='internal'
        )

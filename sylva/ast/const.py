from llvmlite import ir

from .defs import BaseDef


class Const(BaseDef):

    def __init__(self, location, name, value):
        BaseDef.__init__(self, location, name, value.type)
        self.value = value

    def _check_definition(self, module):
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

        const = ir.GlobalVariable(
            module.type.llvm_type, self.type.llvm_type, self.name
        )
        # const.initializer = self.value.emit(obj, module, builder, scope, name)
        const.initializer = ir.Constant(self.type.llvm_type, self.value)
        const.global_constant = True
        return const

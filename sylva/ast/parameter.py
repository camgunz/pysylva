from .bind import Bind


class Parameter(Bind):

    # pylint: disable=unused-argument
    def emit(self, obj, module, builder, scope, name):
        alloca = builder.alloca(self.type.llvm_type, self.name)
        builder.store(obj, alloca)
        scope[self.name] = self
        return obj

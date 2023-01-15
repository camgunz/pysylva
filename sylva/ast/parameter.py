from .bind import Bind


class Parameter(Bind):

    # pylint: disable=unused-argument
    def emit(self, *args, **kwargs):
        scope = kwargs['scope']
        arg = kwargs['arg']
        # I think alloca is only necessary for pointer args?
        # alloca = builder.alloca(self.type.llvm_type, self.name)
        # builder.store(obj, alloca)
        scope[self.name] = arg

        return self

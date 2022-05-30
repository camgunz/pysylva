from .expr import BaseExpr


class CallExpr(BaseExpr):

    def __init__(self, location, function, arguments):
        BaseExpr.__init__(self, location, function.type.return_type)
        self.function = function
        self.arguments = arguments

    # monomorphization_index: int | None = None
    # llvm_function: ir.Function | None = None
    # llvm_arguments: typing.List[ir.Value] | None = None

    def emit(self, obj, module, builder, scope, name):
        return builder.call(
            self.function.emit(module, builder, scope),
            [a.emit(module, builder, scope) for a in self.arguments],
            cconv='fastcc'
        )

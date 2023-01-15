from .expr import BaseExpr


class CallExpr(BaseExpr):

    def __init__(
        self, location, function, arguments, monomorphization_index=0
    ):
        BaseExpr.__init__(self, location, function.type.return_type)
        self.function = function
        self.arguments = arguments
        self.monomorphization_index = monomorphization_index

    # monomorphization_index: int | None = None
    # llvm_function: ir.Function | None = None
    # llvm_arguments: typing.List[ir.Value] | None = None

    def emit(self, *args, **kwargs):
        builder = kwargs['builder']

        func = self.function.emit(*args, **kwargs)

        return builder.call(
            # [TODO] Specify the monomorphization here
            func,
            [a.emit(*args, **kwargs) for a in self.arguments],
            cconv='fastcc'
        )

from attrs import define, field

from .expr import Expr


@define(eq=False, slots=True)
class CallExpr(Expr):
    function = field()
    arguments = field()

    # monomorphization_index: int | None = None
    # llvm_function: ir.Function | None = None
    # llvm_arguments: typing.List[ir.Value] | None = None

    def emit(self, module, builder, scope):
        return builder.call(
            self.function.emit(module, builder, scope),
            [a.emit(module, builder, scope) for a in self.arguments],
            cconv='fastcc'
        )

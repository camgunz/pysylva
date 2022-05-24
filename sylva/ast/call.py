import typing

from attrs import define

from .expr import Expr


@define(eq=False, slots=True)
class CallExpr(Expr):
    function: Expr
    arguments: typing.List[Expr]

    # monomorphization_index: int | None = None
    # llvm_function: ir.Function | None = None
    # llvm_arguments: typing.List[ir.Value] | None = None

    def emit(self, module, builder, scope):
        return builder.call(
            self.function.emit(module, builder, scope),
            [a.emit(module, builder, scope) for a in self.arguments],
            cconv='fastcc'
        )

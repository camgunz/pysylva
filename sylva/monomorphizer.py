from dataclasses import dataclass

from sylva.builtins import CFnValue, FnValue, ParamFnType, SylvaObject
from sylva.expr import CallExpr
from sylva.visitor import Visitor


@dataclass(kw_only=True)
class Monomorphizer(Visitor):

    def add_fn_def(self, name: str, fn: FnValue):
        pass

    def enter_call_expr(
        self, call_expr: CallExpr, name: str, parents: list[SylvaObject]
    ):
        fn_parent: FnValue = next( # type: ignore
            filter(lambda p: isinstance(p, FnValue), reversed(parents))
        )

        if fn_parent.is_var:
            print(f'Skipping generic function {fn_parent.name}')
            return

        # call_expr.function might be a generic function parameter, so...
        # Well, we only want to monomorphize from monomorphized functions, so
        # either we allow walking from here (may weird the algorithm), or we
        # dynamically walk at the top of the loop (have to switch from a
        # `for/in` to... something else. I choose to walk from here.
        fn = call_expr.function.eval(self.module, self.scopes)  # type: ignore
        if fn is None:
            raise Exception(f'No func for {call_expr}')
        if not isinstance(fn, (CFnValue, FnValue)):
            raise Exception(f'{fn} is not a function')
        if not fn.is_var:
            return

        print(f'{fn_parent.name}: Monomorphizing {fn.name} with:')
        for arg in call_expr.arguments:
            print(f'  {arg.type}')
        # monomorphized_fn = fn.type.get_or_create_monomorphization(
        #     name=gen_name('fntype'),
        #     location=call_expr.location,

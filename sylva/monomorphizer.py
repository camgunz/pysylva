from dataclasses import dataclass

from sylva.builtins import (
    CFnValue,
    FnValue,
    ParamFnType,
    SylvaDef,
    SylvaField,
    SylvaObject,
    gen_name,
)
from sylva.expr import CallExpr
from sylva.lookup_expr_type_assigner import LookupExprTypeAssigner
from sylva.mod import Mod
from sylva.visitor import Visitor


@dataclass(kw_only=True)
class Monomorphizer(Visitor):

    def enter_call_expr(
        self, call_expr: CallExpr, name: str, parents: list[SylvaObject | Mod]
    ):
        fn_parent: FnValue = next( # type: ignore
            filter(lambda p: isinstance(p, FnValue), reversed(parents))
        )

        if fn_parent.is_var:
            print(f'Skipping generic function {fn_parent.name}')
            return

        if self.module is None:
            raise Exception('We expect to be inside of a module here')

        fn = call_expr.function.eval(self.scopes)  # type: ignore
        if fn is None:
            raise Exception(f'No func for {call_expr}')
        if not isinstance(fn, (CFnValue, FnValue)):
            raise Exception(f'{fn} is not a function')
        if not isinstance(fn.type, ParamFnType):
            return

        fn_def = SylvaDef(
            module=fn.module,
            name=gen_name(
                fn.name if fn.name else 'fn',
                force_number=bool(fn.name)
            ),
            value=FnValue(
                module=fn.module,
                location=fn.location,
                type=fn.type.get_or_create_monomorphization(
                    module=fn.module,
                    parameters=[  # yapf: ignore
                        SylvaField(
                            module=fn.module,
                            name=p.name,
                            type=a.type
                        )
                        for p, a in zip(
                            fn.type.parameters, call_expr.arguments
                        )
                    ]
                ),
                value=fn.value
            )
        )

        fn.module.add_def(fn_def)

        print(f'Monomorphized {fn_def.name} ({fn_def.module.name})')

        type_assigner = LookupExprTypeAssigner()
        type_assigner.module = fn_def.module
        type_assigner._walk(fn_def.value, name=name, parents=parents)
        self._walk(fn_def.value, name=name, parents=parents)

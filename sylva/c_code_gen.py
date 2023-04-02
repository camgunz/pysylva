from dataclasses import dataclass, field
from io import StringIO

from sylva import errors  # noqa: F401
from sylva.builtins import (
    CFnValue,
    FnValue,
    MonoCArrayType,  # noqa: F401
    MonoCStructType,  # noqa: F401
    MonoCUnionType,  # noqa: F401
    MonoEnumType,  # noqa: F401
    MonoStructType,  # noqa: F401
    MonoVariantType,  # noqa: F401
    SylvaDef,  # noqa: F401
    SylvaObject,  # noqa: F401
    SylvaType,  # noqa: F401
    TypePlaceholder,  # noqa: F401
)
from sylva.expr import CallExpr
from sylva.mod import Mod  # noqa: F401
from sylva.scope import Scope  # noqa: F401
from sylva.stmt import (
    IfBlock,  # noqa: F401
    LetStmt,  # noqa: F401
    LoopBlock,  # noqa: F401
    MatchBlock,  # noqa: F401
    MatchCaseBlock,  # noqa: F401
    ReturnStmt,  # noqa: F401
    WhileBlock,  # noqa: F401
)
from sylva.visitor import Visitor


def prefix(s: str) -> str:
    return f'SYLVA_{s}'


@dataclass(kw_only=True)
class CCodeGen(Visitor):
    _sio: StringIO = field(init=False, default_factory=StringIO)
    _indent_level: int = field(init=False, default=0)
    indentation: str = '  '

    def indent(self):
        self._indent_level += 1

    def dedent(self):
        if self._indent_level == 0:
            raise Exception('Not indented')
        self._indent_level -= 1

    def emit(self, s: str, indent=True):
        if indent:
            self._sio.write('    ' * self._indent_level)
        self._sio.write(s)

    def emit_line(self, line: str):
        self.emit(f'{line}\n')

    def render(self):
        return self._sio.getvalue()

    def reset(self):
        Visitor.reset(self)
        self._sio = StringIO()

    def enter_call_expr(
        self, call_expr: CallExpr, name: str, parents: list[SylvaObject | Mod]
    ):
        fn_parent: FnValue = next( # type: ignore
            filter(lambda p: isinstance(p, FnValue), reversed(parents))
        )

        if fn_parent.is_var:
            return

        fn = call_expr.function.eval(self.scopes)
        fn_name = fn.name if isinstance(fn, CFnValue) else prefix(fn.name)
        self.emit(f'{fn_name}(')

    def exit_call_expr(
        self, call_expr: CallExpr, name: str, parents: list[SylvaObject | Mod]
    ):
        fn_parent: FnValue = next( # type: ignore
            filter(lambda p: isinstance(p, FnValue), reversed(parents))
        )

        if fn_parent.is_var:
            return

        self.emit(');\n', indent=False)

    def enter_fn(self, fn: FnValue, name: str, parents: list[SylvaObject]):
        if fn.is_var:
            return

        Visitor.enter_fn(self, fn, name, parents)

        if not fn.type.return_type:
            self.emit('void ', indent=False)
        else:
            self.emit(f'{fn.type.return_type.name} ', indent=False)

        self._sio.write(f'{prefix(name)}(')

        for n, param in enumerate(fn.type.parameters):
            if n == 0:
                self._sio.write(
                    f'{param.type.name} {param.name}'  # type: ignore
                )
            else:
                self._sio.write(
                    f', {param.type.name} {param.name}'  # type: ignore
                )

        self._sio.write(') {\n')
        self.indent()

    def exit_fn(self, fn: FnValue, name: str, parents: list[SylvaObject]):
        if fn.is_var:
            return

        self.dedent()
        self.emit('}\n\n', indent=False)

    # def if_block(self, if_block: IfBlock):
    #     self.code_block(if_block.code)

    # def impl(self, impl):
    #     pass

    # def let_stmt(self, let_stmt: LetStmt):
    #     pass

    # def loop_block(self, loop_block: LoopBlock):
    #     self.code_block(loop_block.code)

    # def match_block(self, match_block: MatchBlock):
    #     for match_case in match_block.match_cases:
    #         self.match_case_block(match_block, match_case)
    #     if match_block.default_case:
    #         self.default_block(match_block.default_case)

    # def match_case_block(
    #     self,
    #     match_block: MatchBlock,
    #     match_case_block: MatchCaseBlock
    # ):
    #     variant_type = self.expr(match_block.variant_expr)

    #     matching_variant_fields = [
    #         f for f in variant_type.fields # type: ignore
    #         if f.name == match_case_block.variant_field_type_lookup_expr.name
    #     ]
    #     if not matching_variant_fields:
    #         raise errors.NoSuchVariantField(
    #             match_case_block.variant_field_type_lookup_expr.location,
    #             match_case_block.variant_name,
    #             match_case_block.variant_field_type_lookup_expr.name,
    #         )

    #     variant_field = matching_variant_fields[0]

    #     self.scopes.define(match_case_block.variant_name, variant_field.type)

    #     self.code_block(match_case_block.code)

    # def mod(self, module: Mod):
    #     self.module = module
    #     self.funcs = []
    #     self.scopes = Scope()

    #     for d in module.defs.values():
    #         match d:
    #             case SylvaDef():
    #                 match d.value:
    #                     case FnValue():
    #                         self.fn(d.value)
    #             case SylvaType():
    #                 match d.type:
    #                     case MonoCArrayType():
    #                         self.c_array(d.type)
    #                     case MonoCStructType():
    #                         self.c_struct(d.type)
    #                     case MonoCUnionType():
    #                         self.c_union(d.type)
    #                     case MonoEnumType():
    #                         self.enum(d.type)
    #                     case MonoStructType():
    #                         self.struct(d.type)
    #                     case MonoVariantType():
    #                         self.variant(d.type)

    # def range_expr(self, range_expr):
    #     # [TODO] Check that the literal value is the right type and falls
    #     #        within the range
    #     pass

    # def return_stmt(self, return_stmt: ReturnStmt):
    #     func = self.current_func
    #     val = self.expr(return_stmt.expr)

    #     if (isinstance(val, TypePlaceholder) and
    #             isinstance(func.type.return_type, TypePlaceholder)):
    #         if val.name != func.type.return_type.name:
    #             raise errors.MismatchedReturnType(
    #                 return_stmt.expr.location,
    #                 val.name,
    #                 func.type.return_type.name
    #             )
    #     elif val.type != func.type.return_type:
    #         raise errors.MismatchedReturnType(
    #             return_stmt.expr.location,
    #             return_stmt.expr.type,
    #             func.type.return_type
    #         )

    # def struct(self, struct: MonoStructType):
    #     pass

    # def variant(self, variant: MonoVariantType):
    #     pass

    # def struct_expr(self, struct_expr):
    #     pass

    # def type(self, type: SylvaType):
    #     pass

    # def variant_expr(self, variant_expr):
    #     pass

    # def while_block(self, while_block: WhileBlock):
    #     self.code_block(while_block.code)

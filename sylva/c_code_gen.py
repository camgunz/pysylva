from dataclasses import dataclass, field
from io import StringIO

from sylva import errors  # noqa: F401
from sylva.builtins import (
    BOOL,
    CFnValue,  # noqa: F401
    CodeBlock,
    F32,
    F64,
    FnValue,
    I8,
    I16,
    I32,
    I64,
    I128,
    MonoCArrayType,  # noqa: F401
    MonoCFnType,
    MonoCStructType,  # noqa: F401
    MonoCUnionType,  # noqa: F401
    MonoEnumType,  # noqa: F401
    MonoStrType,
    MonoStructType,  # noqa: F401
    MonoVariantType,  # noqa: F401
    NamedSylvaObject,
    RUNE,
    STR,
    StrValue,
    SylvaDef,
    SylvaObject,
    SylvaType,
    SylvaValue,
    TypeDef,
    TypePlaceholder,  # noqa: F401
    U8,
    U16,
    U32,
    U64,
    U128,
)
from sylva.expr import (
    AttributeLookupExpr,
    BinaryExpr,
    BoolLiteralExpr,
    CallExpr,
    CPtrExpr,
    CVoidExpr,
    Expr,
    FloatLiteralExpr,
    IntLiteralExpr,
    LiteralExpr,
    LookupExpr,
    RuneLiteralExpr,
    StrLiteralExpr,
    UnaryExpr,
)
from sylva.mod import Mod  # noqa: F401
from sylva.package import CLibPackage
from sylva.req import Req
from sylva.scope import Scope  # noqa: F401
from sylva.stmt import (
    AssignStmt,
    IfBlock,  # noqa: F401
    LetStmt,  # noqa: F401
    LoopBlock,  # noqa: F401
    MatchBlock,  # noqa: F401
    MatchCaseBlock,  # noqa: F401
    ReturnStmt,  # noqa: F401
    Stmt,
    WhileBlock,  # noqa: F401
)
from sylva.visitor import Visitor


def prefix(obj: LookupExpr | Mod | NamedSylvaObject) -> str:
    return (
        f'SYLVA_{obj.name.replace(".", "_")}'
        if isinstance(obj, Mod)
        else f'SYLVA_{obj.module.name.replace(".", "_")}_{obj.name}'
        if obj.module
        else f'SYLVA_{obj.name}'
    )


@dataclass(kw_only=True)
class CCodeGen(Visitor):
    _sio: StringIO = field(init=False, default_factory=StringIO)
    _indent_level: int = field(init=False, default=0)
    _indent_str: str = field(default='  ')
    indentation: str = '  '

    # [NOTE] Is there some kind of "terminator" logic here, to emit commas
    #        and/or semicolons (...or newlines)?

    def indent(self):
        self._indent_level += 1

    def dedent(self):
        if self._indent_level == 0:
            raise Exception('Not indented')
        self._indent_level -= 1

    def emit(self, s: str, start=False, end=False):
        self._sio.write(self.render(s, start, end))

    def render(self, s: str, start=False, end=False) -> str:
        prefix = self._indent_str * self._indent_level if start else ''
        suffix = ';\n' if end else ''
        return f'{prefix}{s}{suffix}'

    def reset(self):
        Visitor.reset(self)
        self._sio = StringIO()

    def visit(self, module: Mod):
        Visitor.visit(self, module)
        return self._sio.getvalue()

    def render_assign(self, stmt: AssignStmt, start=False, end=False) -> str:
        return self.render(
            f'{stmt.name} = {self.render_expr(stmt.expr)}', start, end
        )

    def render_expr(self, expr: Expr, start=False, end=False) -> str:
        match expr:
            case AttributeLookupExpr():
                obj = (
                    expr.obj.eval(self.scopes)
                    if isinstance(expr.obj, Expr)
                    else expr.obj
                )
                if isinstance(obj, Mod) and obj.type == Mod.Type.C:
                    return self.render(f'{expr.name}', start, end)
                elif isinstance(obj, (SylvaType, FnValue)):
                    return self.render(
                        f'{prefix(obj)}.{expr.name}', start, end
                    )
                else:
                    return self.render(f'{obj}.{expr.name}', start, end)
            case BinaryExpr():
                lhs_s = f'{self.render_expr(expr.lhs)}'
                rhs_s = f'{self.render_expr(expr.rhs)}'
                return self.render(
                    f'{lhs_s} {expr.operator.value} {rhs_s}', start, end
                )
            case BoolLiteralExpr():
                return self.render(str(expr.value.value), start, end)
            case CallExpr():
                args = ', '.join(
                    [self.render_expr(arg) for arg in expr.arguments]
                )
                fn = self.render_expr(expr.function)
                return self.render(f'{fn}({args})', start, end)
            case CPtrExpr():
                if not isinstance(expr.expr, CVoidExpr):
                    return ''
                return self.render(f'((void *)({self.render_expr(expr.expr)}))')
            case CVoidExpr():
                return self.render(f'{self.render_expr(expr.expr)}')
            case FloatLiteralExpr():
                return self.render(str(expr.value.value), start, end)
            case IntLiteralExpr():
                return self.render(str(expr.value.value), start, end)
            case LookupExpr():
                return self.render(expr.name, start, end)
            case RuneLiteralExpr():
                return self.render(f"'{expr.value.value}'", start, end)
            case StrLiteralExpr():
                return self.render(f'"{expr.value.str}"', start, end)
            case UnaryExpr():
                expr_s = f'{self.render_expr(expr.expr)}'
                return self.render(
                    f'{expr.operator.value}{expr_s}', start, end
                )
            case LiteralExpr():
                val = expr.eval(self.scopes)
                return self.render(prefix(val), start, end)
            case _:
                raise ValueError(f'Cannot yet handle {expr}')

    def render_fn(self, fn: FnValue, start=False, finish=False) -> str:
        return_type_name = (
            'void' if not fn.type.return_type else fn.type.return_type.name
        )
        fn_name = prefix(fn)
        param_type_names = ', '.join([
            f'{prefix(param.type)} {param.name}' # type: ignore
            for param in fn.type.parameters
        ])

        return f'{return_type_name} {fn_name}({param_type_names})'

    def render_requirement(self, req: Req, start=False, end=False) -> str:
        mod = req.module
        sio = StringIO()

        if isinstance(mod.package, CLibPackage):
            includes = [f'#include "{hf}"' for hf in mod.package.header_files]
            sio.write('\n'.join(includes) + '\n')

            for d in mod.defs.values():
                if not isinstance(d, TypeDef):
                    continue
                if d.name == d.type.name:
                    continue
                if d.from_c:
                    continue
                sio.write(f'typedef {d.type.name} {d.name};\n')

            sio.write('\n')

            for d in mod.defs.values():
                if not isinstance(d, SylvaDef):
                    continue
                if isinstance(d.type, MonoCFnType):
                    continue
                if d.sylva_only:
                    continue
                val = self.render_value(d.value, end=True)
                sio.write(f'static {prefix(d.type)} {d.name} = {val}')

            sio.write('\n')

        return sio.getvalue()


    def render_stmt(self, stmt: Stmt, start=False, end=False) -> str:
        return ''

    def render_value(self, value: SylvaValue, start=False, end=False) -> str:
        match value:
            case StrValue():
                return self.render(f'"{value.str}"', start, end)
            case _:
                return self.render(f"{value.value}", start, end)

    def enter_code_block(
        self, code_block: CodeBlock, name: str, parents: list[SylvaObject | Mod]
    ) -> bool:
        Visitor.enter_code_block(self, code_block, name, parents)
        self.emit(' {\n')
        self.indent()
        for node in code_block.code:
            match node:
                case Expr():
                    self.emit(self.render_expr(node, start=True, end=True))
                case Stmt():
                    self.emit(self.render_stmt(node, start=True, end=True))
        return True

    def exit_code_block(
        self, code_block: CodeBlock, name: str, parents: list[SylvaObject | Mod]
    ) -> bool:
        self.dedent()
        self.emit('}\n\n', start=True)

        return True

    def enter_fn(
        self, fn: FnValue, name: str, parents: list[SylvaObject | Mod]
    ) -> bool:
        if fn.is_var:
            return False

        Visitor.enter_fn(self, fn, name, parents)

        self.emit(self.render_fn(fn, start=True))

        return True

    def enter_mod(
        self,
        mod: Mod,
        name: str,
        parents: list[SylvaObject | Mod],
    ) -> bool:
        Visitor.enter_mod(self, mod, name, parents)

        for req in mod.requirements.values():
            self.emit(self.render_requirement(req))

        self.emit(f'typedef int8_t {prefix(I8)}', end=True)
        self.emit(f'typedef uint8_t {prefix(U8)}', end=True)
        self.emit(f'typedef int16_t {prefix(I16)}', end=True)
        self.emit(f'typedef uint16_t {prefix(U16)}', end=True)
        self.emit(f'typedef int32_t {prefix(I32)}', end=True)
        self.emit(f'typedef uint32_t {prefix(U32)}', end=True)
        self.emit(f'typedef int64_t {prefix(I64)}', end=True)
        self.emit(f'typedef uint64_t {prefix(U64)}', end=True)
        # self.emit(f'typedef int128_t {prefix(I128)}', end=True)
        # self.emit(f'typedef uint128_t {prefix(U128)}', end=True)
        self.emit(f'typedef bool {prefix(BOOL)}', end=True)
        self.emit(f'typedef uint32_t {prefix(RUNE)}', end=True)
        self.emit(f'typedef float {prefix(F32)}', end=True)
        self.emit(f'typedef double {prefix(F64)}', end=True)
        self.emit(f'typedef const char * {prefix(STR)}', end=True)
        self.emit('\n')

        return True

    def enter_str_type(
        self,
        stype: MonoStrType,
        name: str,
        parents: list[SylvaObject | Mod],
    ) -> bool:
        breakpoint()
        return True

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

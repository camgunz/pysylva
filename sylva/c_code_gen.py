from contextlib import contextmanager
from dataclasses import dataclass, field
from io import StringIO

from sylva import errors
from sylva.builtins import (
    FnValue,
    MonoCArrayType,
    MonoCStructType,
    MonoCUnionType,
    MonoEnumType,
    MonoStructType,
    MonoVariantType,
    SylvaDef,
    SylvaObject,
    SylvaType,
    TypePlaceholder,
)
from sylva.mod import Mod
from sylva.scope import Scope
from sylva.stmt import (
    IfBlock,
    LetStmt,
    LoopBlock,
    MatchBlock,
    MatchCaseBlock,
    ReturnStmt,
    WhileBlock,
)
from sylva.visitor import Visitor


@dataclass(kw_only=True)
class CCodeGen(Visitor):
    _sio: StringIO = field(init=False, default_factory=StringIO)
    _indent_level: int = field(init=False, default=0)
    indentation: str = '  '

    def indent(self):
        self._indent_level += 1

    def deindent(self):
        if self._indent_level == 0:
            raise Exception('Not indented')
        self._indent_level -= 1

    def emit(self, s: str):
        self._sio.write(s)

    def emit_indent(self):
        self.emit('  ' * self._indent)

    def emit_line(self, line: str):
        self.emit_indent()
        self.emit(f'{line}\n')

    def enter_fn(self, fn: FnValue, name: str, parents: list[SylvaObject]):
        if not fn.type.return_type:
            self.emit('void ')
        else:
            self.emit(f'{fn.type.return_type.name}')

        self._sio.write(f'{name} (')

        for n, param in enumerate(fn.type.parameters):
            if n == 0:
                self._sio.write(f'{self.type(param.type)} {param.name}')
            else:
                self._sio.write(f', {self.type(param.type)} {param.name}')

        with (self.new_func(fn), self.new_scope()):
            for param in fn.type.parameters:
                if isinstance(param.type, SylvaType):
                    self.define(param.name, param.type)
            self.code_block(fn.value)

    def exit_fn(self, fn: FnValue, name: str, parents: list[SylvaObject]):
        self.emit('}')
        self.deindent()

    def if_block(self, if_block: IfBlock):
        self.code_block(if_block.code)

    def impl(self, impl):
        pass

    def let_stmt(self, let_stmt: LetStmt):
        pass

    def loop_block(self, loop_block: LoopBlock):
        self.code_block(loop_block.code)

    def match_block(self, match_block: MatchBlock):
        for match_case in match_block.match_cases:
            self.match_case_block(match_block, match_case)
        if match_block.default_case:
            self.default_block(match_block.default_case)

    def match_case_block(
        self,
        match_block: MatchBlock,
        match_case_block: MatchCaseBlock
    ):
        variant_type = self.expr(match_block.variant_expr)

        matching_variant_fields = [
            f for f in variant_type.fields # type: ignore
            if f.name == match_case_block.variant_field_type_lookup_expr.name
        ]
        if not matching_variant_fields:
            raise errors.NoSuchVariantField(
                match_case_block.variant_field_type_lookup_expr.location,
                match_case_block.variant_name,
                match_case_block.variant_field_type_lookup_expr.name,
            )

        variant_field = matching_variant_fields[0]

        self.scopes.define(match_case_block.variant_name, variant_field.type)

        self.code_block(match_case_block.code)

    def mod(self, module: Mod):
        self.module = module
        self.funcs = []
        self.scopes = Scope()

        for d in module.defs.values():
            match d:
                case SylvaDef():
                    match d.value:
                        case FnValue():
                            self.fn(d.value)
                case SylvaType():
                    match d.type:
                        case MonoCArrayType():
                            self.c_array(d.type)
                        case MonoCStructType():
                            self.c_struct(d.type)
                        case MonoCUnionType():
                            self.c_union(d.type)
                        case MonoEnumType():
                            self.enum(d.type)
                        case MonoStructType():
                            self.struct(d.type)
                        case MonoVariantType():
                            self.variant(d.type)

    def range_expr(self, range_expr):
        # [TODO] Check that the literal value is the right type and falls
        #        within the range
        pass

    def return_stmt(self, return_stmt: ReturnStmt):
        func = self.current_func
        val = self.expr(return_stmt.expr)

        if (isinstance(val, TypePlaceholder) and
                isinstance(func.type.return_type, TypePlaceholder)):
            if val.name != func.type.return_type.name:
                raise errors.MismatchedReturnType(
                    return_stmt.expr.location,
                    val.name,
                    func.type.return_type.name
                )
        elif val.type != func.type.return_type:
            raise errors.MismatchedReturnType(
                return_stmt.expr.location,
                return_stmt.expr.type,
                func.type.return_type
            )

    def struct(self, struct: MonoStructType):
        pass

    def variant(self, variant: MonoVariantType):
        pass

    def struct_expr(self, struct_expr):
        pass

    def type(self, type: SylvaType):
        pass

    def variant_expr(self, variant_expr):
        pass

    def while_block(self, while_block: WhileBlock):
        self.code_block(while_block.code)

from contextlib import contextmanager
from dataclasses import dataclass, field

from sylva import errors
from sylva.builtins import (
    CodeBlock,
    FnValue,
    SylvaObject,
    SylvaType,
    SylvaValue,
    TypePlaceholder,
)
from sylva.expr import Expr, LookupExpr
from sylva.mod import Mod
from sylva.scope import Scope
from sylva.stmt import (
    AssignStmt,
    LetStmt,
    MatchBlock,
    MatchCaseBlock,
    ReturnStmt,
)


@dataclass(kw_only=True)
class TypeChecker:
    module: Mod | None = field(init=False, default=None)
    funcs: list[FnValue] = field(init=False, default_factory=list)
    scopes: Scope = field(init=False, default_factory=Scope)

    # [TODO]
    # - Default args for structs/variants
    # - Const defs/arrays/structs/variants

    @contextmanager
    def new_scope(self):
        self.scopes.push()
        yield
        self.scopes.pop()

    @contextmanager
    def new_func(self, fn: FnValue):
        self.funcs.append(fn)
        yield
        self.funcs.pop()

    @property
    def current_func(self):
        if not self.funcs:
            raise Exception('Not within a function')
        return self.funcs[0]

    def define(self, name: str, type: SylvaType):
        self.scopes.define(name, type)

    def get_expr_type(self, expr: Expr):
        match expr:
            case LookupExpr():
                val = self.lookup(expr.name)
                if val is None:
                    raise errors.UndefinedSymbol(expr.location, expr.name)
                expr.type = val.type
                return val.type
            case _:
                return expr.type

    def lookup(self, name: str):
        t = self.scopes.lookup(name)
        if t is not None:
            return t

        if self.module is None:
            raise Exception('self.module is somehow none')

        val = self.module.lookup(name)
        if val is None:
            return None

        match val:
            case Mod():
                return Mod # [NOTE] WTF haha
            case SylvaValue(type=t):
                return t
            case SylvaType():
                return val

    def enter_assign_stmt(
        self, assign_stmt: AssignStmt, parents: list[SylvaObject]
    ):
        # [TODO] Handle things like struct field assignment
        var_type = self.lookup(assign_stmt.name)

        if var_type is None:
            raise errors.UndefinedSymbol(
                assign_stmt.location, assign_stmt.name
            )

        if assign_stmt.expr.type != var_type:
            raise errors.MismatchedVariableType(
                assign_stmt.expr.location,
                assign_stmt.expr.type,
                var_type
            )

        # [TODO] Ensure expr's type isn't an aggregate value, requiring an
        #        aggregate deep copy
        # [TODO] Ensure var's type isn't an aggregate

    def enter_code_block(
        self, code_block: CodeBlock, parents: list[SylvaObject]
    ):
        self.scopes.push()

    def exit_code_block(
        self, code_block: CodeBlock, parents: list[SylvaObject]
    ):
        self.scopes.pop()

    def enter_lookup_expr(
        self, lookup_expr: LookupExpr, parents: list[SylvaObject]
    ):
        val = self.lookup(lookup_expr.name)
        if val is None:
            raise errors.UndefinedSymbol(
                lookup_expr.location, lookup_expr.name
            )
        return val

    def enter_fn(self, fn: FnValue, parents: list[SylvaObject]):
        # [TODO] Keep track of references to values with type params so we can
        #        build call constraints
        with (self.new_func(fn), self.new_scope()):
            for param in fn.type.parameters:
                if isinstance(param.type, SylvaType):
                    self.define(param.name, param.type)

    def enter_let_stmt(self, let_stmt: LetStmt, parents: list[SylvaObject]):
        self.scopes.define(let_stmt.name, let_stmt.expr.type)

    def enter_match_case_block(
        self,
        match_case_block: MatchCaseBlock,
        parents: list[SylvaObject],
    ):
        match_block = parents[-1]

        if not isinstance(match_block, MatchBlock):
            raise TypeError('Match case block without match block')

        variant_type = self.get_expr_type(match_block.variant_expr)

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

    def enter_mod(self, module: Mod, parents: list[SylvaObject]):
        self.module = module
        self.funcs = []
        self.scopes = Scope()

    def enter_return_stmt(self, return_stmt: ReturnStmt, parents: list[SylvaObject]):
        func = self.current_func
        val_type = self.get_expr_type(return_stmt.expr)

        if (isinstance(val_type, TypePlaceholder) and
                isinstance(func.type.return_type, TypePlaceholder)):
            if val_type.name != func.type.return_type.name:
                raise errors.MismatchedReturnType(
                    return_stmt.expr.location,
                    val_type.name,
                    func.type.return_type.name
                )
        elif val_type.type != func.type.return_type:
            raise errors.MismatchedReturnType(
                return_stmt.expr.location,
                return_stmt.expr.type,
                func.type.return_type
            )

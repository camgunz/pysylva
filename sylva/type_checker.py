from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Optional

from sylva import errors
from sylva.builtins import (
    CodeBlock,
    FnValue,
    MonoCArrayType,
    MonoCStructType,
    MonoCUnionType,
    MonoEnumType,
    MonoStructType,
    MonoVariantType,
    SylvaDef,
    SylvaType,
    SylvaValue,
    TypePlaceholder,
)
from sylva.expr import Expr, LookupExpr
from sylva.mod import Mod
from sylva.scope import Scope
from sylva.stmt import (
    AssignStmt,
    DefaultBlock,
    IfBlock,
    LetStmt,
    LoopBlock,
    MatchBlock,
    MatchCaseBlock,
    ReturnStmt,
    WhileBlock,
)


@dataclass(kw_only=True)
class TypeChecker:
    module: Optional[Mod] = field(init=False, default=None)
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

    def array_expr(self, array_expr):
        pass

    def assign_stmt(self, assign_stmt: AssignStmt):
        # [TODO] Handle things like struct field assignment
        var_type = self.lookup(assign_stmt.name)

        if var_type is None:
            raise errors.UndefinedSymbol(assign_stmt.location, assign_stmt.name)

        if assign_stmt.expr.type != var_type:
            raise errors.MismatchedVariableType(
                assign_stmt.expr.location,
                assign_stmt.expr.type,
                var_type
            )

        # [TODO] Ensure expr's type isn't an aggregate value, requiring an
        #        aggregate deep copy
        # [TODO] Ensure var's type isn't an aggregate
        pass

    def c_array(self, c_array: MonoCArrayType):
        pass

    def c_struct(self, c_struct: MonoCStructType):
        pass

    def c_union(self, c_union: MonoCUnionType):
        pass

    def code_block(self, code_block: CodeBlock):
        with self.new_scope():
            for node in code_block.code:
                match node:
                    case IfBlock():
                        self.if_block(node)
                    # case SwitchBlock:
                    #     pass
                    case MatchBlock():
                        self.match_block(node)
                    # case ForBlock:
                    #     pass
                    case WhileBlock():
                        self.while_block(node)
                    case LoopBlock():
                        self.loop_block(node)
                    case LetStmt():
                        self.let_stmt(node)
                    case AssignStmt():
                        self.assign_stmt(node)
                    case ReturnStmt():
                        self.return_stmt(node)
                    case Expr():
                        self.expr(node)

    def default_block(self, default_block: DefaultBlock):
        self.code_block(default_block.code)

    def enum(self, enum: MonoEnumType):
        pass

    def expr(self, expr: Expr):
        match expr:
            case LookupExpr():
                val = self.lookup(expr.name)
                if val is None:
                    raise errors.UndefinedSymbol(expr.location, expr.name)
                return val


    def fn(self, fn: FnValue):
        # [TODO] Keep track of references to values with type params so we can
        #        build call constraints
        with (self.new_func(fn), self.new_scope()):
            for param in fn.type.parameters:
                if isinstance(param.type, SylvaType):
                    self.define(param.name, param.type)
            self.code_block(fn.value)

    def if_block(self, if_block: IfBlock):
        self.code_block(if_block.code)

    def impl(self, impl):
        # [TODO] Type check each function
        pass

    def let_stmt(self, let_stmt: LetStmt):
        self.scopes.define(let_stmt.name, let_stmt.expr.type)

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

    def variant_expr(self, variant_expr):
        pass

    def while_block(self, while_block: WhileBlock):
        self.code_block(while_block.code)

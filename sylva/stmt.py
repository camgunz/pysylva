from dataclasses import dataclass, field
from typing import Optional

from sylva.code_block import CodeBlock
from sylva.expr import Expr, VariantFieldTypeLookupExpr
from sylva.builtins import SylvaObject


@dataclass(kw_only=True)
class Stmt(SylvaObject):
    pass


@dataclass(kw_only=True)
class StmtBlock(Stmt):
    code: CodeBlock


@dataclass(kw_only=True)
class LetStmt(Stmt):
    name: str
    expr: Expr


@dataclass(kw_only=True)
class AssignStmt(Stmt):
    name: str
    expr: Expr


@dataclass(kw_only=True)
class BreakStmt(Stmt):
    pass


@dataclass(kw_only=True)
class ContinueStmt(Stmt):
    pass


@dataclass(kw_only=True)
class ReturnStmt(Stmt):
    expr: Expr


@dataclass(kw_only=True)
class IfBlock(StmtBlock):
    conditional_expr: Expr
    else_code: CodeBlock


@dataclass(kw_only=True)
class LoopBlock(StmtBlock):
    pass


@dataclass(kw_only=True)
class WhileBlock(StmtBlock):
    conditional_expr: Expr


@dataclass(kw_only=True)
class MatchCaseBlock(StmtBlock):
    variant_name: str
    variant_field_type_lookup_expr: VariantFieldTypeLookupExpr


@dataclass(kw_only=True)
class DefaultBlock(StmtBlock):
    pass


@dataclass(kw_only=True)
class MatchBlock(Stmt):
    variant_expr: Expr
    match_cases: list[MatchCaseBlock] = field(default_factory=list)
    default_case: Optional[DefaultBlock] = None
